# dj_palette/templatetags/palette_tags.py
from functools import lru_cache
import os, re
from django import template
from django.template import Node, NodeList, TemplateSyntaxError, loader, Context, VariableDoesNotExist
from django.template.base import TokenType
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True, name="back_button")
def back_button(context):
    path = context['request'].path
    # Matches /admin/app/model/add/
    m = re.match(r'^/admin/([^/]+)/([^/]+)/add/$', path)
    if m:
        app, model = m.groups()
        return f"/admin/{app}/{model}/"
    # Matches /admin/app/model/pk/change/
    m = re.match(r'^/admin/([^/]+)/([^/]+)/\d+/change/$', path)
    if m:
        app, model = m.groups()
        return f"/admin/{app}/{model}/"
    # Matches /admin/app/model/
    m = re.match(r'^/admin/([^/]+)/([^/]+)/$', path)
    if m:
        app = m.group(1)
        return f"/admin/{app}/"
    # Default: admin index
    return reverse('admin:index')


@register.filter(name='render_ui')
def render_ui(component_name, props_str=""):
    props_dict = {}
    try:
        for item in props_str.split(";"):
            if item.strip():
                key, val = item.split(":", 1)
                props_dict[key.strip()] = val.strip()
    except Exception as e:
        props_dict["error"] = str(e)
    return render_to_string(f"palette/components/{component_name}.html", {"props": props_dict})

@register.filter
def widget_type(field):
    print("FIeld", field.field.widget_type)
    return field.field.widget_type



@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})



# -------------------------
# Helpers: AST walker
# -------------------------
def _iter_nodelist_recursive(nodelist):
    """Yield nodes recursively from a NodeList."""
    for node in nodelist:
        yield node
        # common attributes that hold NodeList children
        for attr in ("nodelist", "nodelist_true", "nodelist_false", "nodelist_loop"):
            child = getattr(node, attr, None)
            if isinstance(child, NodeList):
                yield from _iter_nodelist_recursive(child)

# -------------------------
# Palette Block Context (keeps block stacks) - stored in render_context
# -------------------------
class PaletteBlockContext:
    """Small stack-based container for block nodelists per block name."""
    def __init__(self):
        self.blocks = {}  # name -> [nodelist_top, nodelist_next, ...]

    def add_block(self, name, nodelist, prepend=False):
        stack = self.blocks.setdefault(name, [])
        if prepend:
            stack.insert(0, nodelist)
        else:
            stack.append(nodelist)

    def push_override(self, name, nodelist):
        self.add_block(name, nodelist, prepend=True)

    def get_stack(self, name):
        return self.blocks.get(name, [])

    def get_top(self, name):
        s = self.get_stack(name)
        return s[0] if s else None

    def extend_from(self, other):
        """Append parent's stacks after ours so ours take precedence."""
        for name, stack in getattr(other, "blocks", {}).items():
            ours = self.blocks.setdefault(name, [])
            ours.extend(stack)

# -------------------------
# Node definitions
# -------------------------
class PaletteBlockNode(Node):
    """{% palette_block name %} ... {% endpalette_block %}"""
    def __init__(self, name, nodelist):
        self.block_name = name
        self.nodelist = nodelist

    def render(self, context):
        """
        Renders the topmost block for this name from the PaletteBlockContext
        in context.render_context['palette_block_context'] if available.
        Supports {{ block.super }} by using a small helper object `block` in the
        rendering context whose `.super` property renders the next-in-stack.
        """
        pbc = context.render_context.get("palette_block_context")
        if not pbc:
            # No palette environment installed -> fallback to rendering this node's nodelist
            return self.nodelist.render(context)

        stack = pbc.get_stack(self.block_name)
        if not stack:
            # nothing registered anywhere -> fallback to this node
            return self.nodelist.render(context)

        # We'll render stack[0] (top) and support block.super to render stack[1], etc.
        class _BlockSuper:
            def __init__(self, ctx, stack, index):
                self._ctx = ctx
                self._stack = stack
                self._index = index

            @property
            def super(self):
                next_index = self._index + 1
                if next_index >= len(self._stack):
                    return ""
                next_nodelist = self._stack[next_index]
                # render next_nodelist with a temporary block pointer to next_index
                prev_block = self._ctx.get('block', None)
                self._ctx['block'] = _BlockSuper(self._ctx, self._stack, next_index)
                try:
                    return next_nodelist.render(self._ctx)
                finally:
                    # restore prev block variable
                    if prev_block is None:
                        try:
                            del self._ctx['block']
                        except Exception:
                            pass
                    else:
                        self._ctx['block'] = prev_block

        top_nodelist = stack[0]
        prev_block = context.get('block', None)
        context['block'] = _BlockSuper(context, stack, 0)
        try:
            return top_nodelist.render(context)
        finally:
            # restore original 'block' variable
            if prev_block is None:
                try:
                    del context['block']
                except Exception:
                    pass
            else:
                context['block'] = prev_block

@register.tag("palette_block")
def do_palette_block(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("palette_block takes exactly one argument: the block name")
    name = bits[1]
    nodelist = parser.parse(('endpalette_block',))
    parser.delete_first_token()
    return PaletteBlockNode(name, nodelist)


class PaletteComponentDefNode(Node):
    """
    {% palette_component name %}
       ... contains palette_block nodes ...
    {% endpalette_component %}

    At render time the node registers itself into context.render_context['palette_registry']
    keyed by the template origin/name. This avoids cross-import module globals.
    """
    def __init__(self, name, nodelist):
        self.component_name = name
        self.nodelist = nodelist

    def render(self, context):
        # store registration in render_context registry (per-render)
        registry = context.render_context.setdefault("palette_registry", {})
        # Determine a key for this template file. Prefer parser origin name if available.
        # We can attempt to find the current template origin from context; if not available,
        # fallback to a generic key (component-maybe-ambiguous).
        tpl_key = None
        # Attempt: Django often stores the current template name on the context.template attribute
        tpl_obj = getattr(context, "template", None)
        if tpl_obj:
            tpl_key = getattr(tpl_obj, "name", None) or getattr(getattr(tpl_obj, "origin", None), "name", None)
        if not tpl_key:
            # fallback: use the component name as a poor-man's key (less ideal but safe)
            tpl_key = "inline:" + self.component_name

        comp_dict = registry.setdefault(tpl_key, {})
        comp_dict[self.component_name] = self.nodelist

        # also expose registry to main context for debugging convenience
        try:
            context["PALETTE_COMPONENTS"] = registry
        except Exception:
            # context may be a RequestContext-like object; best-effort only
            pass

        # definition-only: emit nothing
        return ""

@register.tag("palette_component")
def do_palette_component(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("palette_component requires exactly one name argument")
    raw = bits[1]
    if raw and raw[0] in ('"', "'") and raw[-1] == raw[0]:
        name = raw[1:-1]
    else:
        name = raw
    nodelist = parser.parse(('endpalette_component',))
    parser.delete_first_token()
    return PaletteComponentDefNode(name, nodelist)


class PaletteExtendsNode(Node):
    """{% palette_extends "parent.html" %} marker (literal parent name for now)"""
    def __init__(self, parent_name):
        self.parent_name = parent_name

    def render(self, context):
        return ""

@register.tag("palette_extends")
def do_palette_extends(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("palette_extends takes a single (quoted) parent template name")
    parent = bits[1]
    if parent and parent[0] in ('"', "'") and parent[-1] == parent[0]:
        parent = parent[1:-1]
    else:
        raise TemplateSyntaxError("palette_extends requires a quoted literal parent template name")
    return PaletteExtendsNode(parent)


class PaletteOverrideNode(Node):
    """Used inside palette_ui body to declare overrides for blocks."""
    def __init__(self, name, nodelist):
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        return ""

@register.tag("palette_override")
def do_palette_override(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("palette_override requires exactly one name argument")
    name = bits[1]
    nodelist = parser.parse(('endpalette_override',))
    parser.delete_first_token()
    return PaletteOverrideNode(name, nodelist)


# -------------------------
# Helper: index template components (cached)
# -------------------------
@lru_cache(maxsize=256)
def _index_template_components(template_name):
    """
    Returns { 'components': {name: node}, 'parent': parent_name_or_None }
    Uses loader.get_template to obtain the compiled Template object and scans its nodelist.
    """
    try:
        tpl = loader.get_template(template_name)
    except Exception as e:
        raise TemplateSyntaxError(f"palette_ui: cannot load template '{template_name}': {e}")

    root = getattr(tpl, "nodelist", None) or (getattr(tpl, "template", None) and getattr(tpl.template, "nodelist", None))
    comps = {}
    parent = None
    if root:
        for node in _iter_nodelist_recursive(root):
            if isinstance(node, PaletteComponentDefNode):
                comps[node.component_name] = node
            elif isinstance(node, PaletteExtendsNode) and parent is None:
                parent = node.parent_name
    return {"components": comps, "parent": parent}


def clear_palette_cache():
    _index_template_components.cache_clear()


# -------------------------
# Renderer: palette_ui tag
# -------------------------
class PaletteUIRenderNode(Node):
    def __init__(self, file_token, component_name, with_vars, inner_nodelist):
        # file_token: literal string or a FilterExpression (we accept both)
        self.file_token = file_token
        self.component_name = component_name
        self.with_vars = with_vars  # dict name -> FilterExpression
        self.inner_nodelist = inner_nodelist  # contains palette_override nodes

    @staticmethod
    def _resolve_file_token(token, context):
        # token may be a literal string (e.g. "palette/components/card.html") or a FilterExpression
        if hasattr(token, "resolve"):
            return token.resolve(context)
        return token

    def _collect_user_overrides(self, context):
        overrides = {}
        for node in _iter_nodelist_recursive(self.inner_nodelist):
            if isinstance(node, PaletteOverrideNode):
                overrides[node.name] = node.nodelist
        return overrides

    def _build_palette_block_context_for_component(self, start_template_name):
        """
        Build a PaletteBlockContext for this component by scanning the start_template_name
        and optionally following palette_extends parent chain. The result contains all base
        blocks for the component (child's blocks appear earlier).
        """
        visited = set()
        current = start_template_name
        merged = PaletteBlockContext()
        while current and current not in visited:
            visited.add(current)
            try:
                idx = _index_template_components(current)
            except TemplateSyntaxError:
                break
            comps = idx.get("components", {})
            if self.component_name in comps:
                comp_node = comps[self.component_name]
                # scan comp_node.nodelist for palette_block nodes and add them
                for n in _iter_nodelist_recursive(comp_node.nodelist):
                    if isinstance(n, PaletteBlockNode):
                        # append (lower precedence) - child's blocks will be encountered earlier in chain
                        merged.add_block(n.block_name, n.nodelist, prepend=False)
            parent = idx.get("parent")
            if not parent:
                break
            current = parent
        return merged

    def render(self, context):
        # Resolve file token to template name
        try:
            tpl_name = self._resolve_file_token(self.file_token, context)
        except Exception as e:
            return f"<!-- palette_ui error resolving file: {e} -->"

        comp_name = self.component_name

        # Resolve props
        local_vars = {}
        for k, expr in self.with_vars.items():
            try:
                local_vars[k] = expr.resolve(context)
            except Exception:
                local_vars[k] = None

        # Attempt to find the component nodelist by trying multiple strategies,
        # but crucially read/write the registry out of context.render_context
        registry = context.render_context.setdefault("palette_registry", {})

        comp_nodelist = None
        origin_key = None

        # 1) direct registry lookup by tpl_name
        comp_nodelist = registry.get(tpl_name, {}).get(comp_name)
        if comp_nodelist:
            origin_key = tpl_name

        # 2) try loader's template name variants
        if not comp_nodelist:
            try:
                tpl_obj = loader.get_template(tpl_name)
            except Exception as e:
                return f"<!-- palette_ui: cannot load template '{tpl_name}': {e} -->"
            tpl_key = getattr(tpl_obj, "name", None) or getattr(getattr(tpl_obj, "origin", None), "name", None)
            if tpl_key:
                comp_nodelist = registry.get(tpl_key, {}).get(comp_name)
                if comp_nodelist:
                    origin_key = tpl_key

        # 3) try basename matching
        if not comp_nodelist:
            tpl_basename = os.path.basename(tpl_name)
            for key in registry.keys():
                if os.path.basename(key) == tpl_basename:
                    comp_nodelist = registry.get(key, {}).get(comp_name)
                    if comp_nodelist:
                        origin_key = key
                        break

        # 4) fallback: scan AST (and register found component into registry under tpl_name)
        if not comp_nodelist:
            try:
                idx = _index_template_components(tpl_name)
            except TemplateSyntaxError:
                idx = None
            if idx and comp_name in idx.get("components", {}):
                node = idx["components"][comp_name]
                comp_nodelist = node.nodelist
                registry.setdefault(tpl_name, {})[comp_name] = comp_nodelist
                origin_key = tpl_name

        if not comp_nodelist:
            return f"<!-- palette_ui: component '{comp_name}' not found in template '{tpl_name}' -->"

        # Build the palette block context by following palette_extends chain so that parent blocks
        # get appended after child blocks (child precedence)
        palette_block_ctx = self._build_palette_block_context_for_component(origin_key)

        # collect user overrides from inner_nodelist (user-supplied palette_override tags)
        user_overrides = self._collect_user_overrides(context)
        for name, nlist in user_overrides.items():
            palette_block_ctx.push_override(name, nlist)

        # Install the palette block context into render_context for PaletteBlockNode to consult
        prev_pbc = context.render_context.get("palette_block_context", None)
        context.render_context["palette_block_context"] = palette_block_ctx

        # Also expose the registry for debugging via template variable PALETTE_COMPONENTS
        try:
            context["PALETTE_COMPONENTS"] = registry
        except Exception:
            pass

        # Push a new variable context, inject props, render the component nodelist directly,
        # then pop and restore render_context entries.
        context.push()
        try:
            for k, v in local_vars.items():
                context[k] = v
            # also inject `children` as the inner nodelist rendered (render-prop slot)
            context["children"] = self.inner_nodelist.render(context)

            rendered = comp_nodelist.render(context)
        finally:
            context.pop()
            # restore previous palette_block_context
            if prev_pbc is None:
                context.render_context.pop("palette_block_context", None)
            else:
                context.render_context["palette_block_context"] = prev_pbc

        return mark_safe(rendered)

@register.tag("palette_ui")
def do_palette_ui(parser, token):
    """
    Grammar:
      {% palette_ui file="path" component="name" with key=expr key2=expr2 %}
         {% palette_override blockname %}...{% endpalette_override %}
      {% endpalette_ui %}
    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("palette_ui requires file= and component= keyword arguments")

    file_token = None
    component_name = None
    with_vars = {}

    i = 1
    while i < len(bits):
        b = bits[i]
        if b == "with":
            i += 1
            break
        if "=" not in b:
            raise TemplateSyntaxError("palette_ui expects keyword args like file=\"...\" component=\"...\"")
        key, val = b.split("=", 1)
        if key == "file":
            # keep literal string or compile_filter for expression
            if val and val[0] in ('"', "'") and val[-1] == val[0]:
                file_token = val[1:-1]
            else:
                file_token = parser.compile_filter(val)
        elif key == "component":
            if val and val[0] in ('"', "'") and val[-1] == val[0]:
                component_name = val[1:-1]
            else:
                # allow variable -> store as raw token to resolve in render
                component_name = val
        else:
            # treat as an immediate with var
            with_vars[key] = parser.compile_filter(val)
        i += 1

    # parse remaining with k=v pairs
    while i < len(bits):
        pair = bits[i]
        if "=" not in pair:
            raise TemplateSyntaxError("Invalid with arg in palette_ui; expected key=value")
        k, v = pair.split("=", 1)
        with_vars[k] = parser.compile_filter(v)
        i += 1

    if not file_token or not component_name:
        raise TemplateSyntaxError("palette_ui requires file= and component= arguments")

    inner_nodelist = parser.parse(('endpalette_ui',))
    parser.delete_first_token()
    return PaletteUIRenderNode(file_token, component_name, with_vars, inner_nodelist)
