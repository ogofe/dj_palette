# dj_palette/templatetags/palette.py
"""
Palette Template Engine - Custom Django Template Tags
======================================================

A component-based template system for Django with support for:
- Reusable components (palette_component)
- Overridable slots (palette_block)
- Component composition (palette_ui)
- Context-aware rendering with proper scoping
"""

import os
import re
from django import template
from django.template import (
    Node,
    NodeList,
    TemplateSyntaxError,
    loader,
    Context as TempContext,
)
from django.template.base import Parser, Token, token_kwargs
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.template.loader import render_to_string


register = template.Library()

@register.filter('dir')
def dir_filter(obj):
    return f"{dir(obj)}"


# ========================
# AST WALKING HELPERS
# ========================

def _iter_nodelist_recursive(nodelist):
    """
    Walk a NodeList recursively, yielding all nodes including children.
    
    Supports nested structures:
    - nodelist: standard child list
    - nodelist_true/nodelist_false: if/else branches
    - nodelist_loop: for loops
    """
    for node in nodelist:
        yield node
        for attr in ("nodelist", "nodelist_true", "nodelist_false", "nodelist_loop"):
            child = getattr(node, attr, None)
            if isinstance(child, NodeList):
                yield from _iter_nodelist_recursive(child)


# ========================
# PALETTE_OVERRIDE NODE
# ========================

class PaletteOverrideNode(Node):
    """
    Represents an override block for a palette_block slot.
    
    Structure:
        {% palette_override block_name %}
            ... override content ...
        {% endpalette_override %}
    
    The override content is not rendered directly; instead, it's collected
    by palette_ui and applied when the component is rendered.
    """

    def __init__(self, name, nodelist):
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        # Overrides are never rendered directly; they're processed by palette_ui
        return ""


@register.tag("palette_override")
def do_palette_override(parser, token):
    """Parse a palette_override tag."""
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError(
            "palette_override requires exactly one argument: the block name"
        )
    
    block_name = bits[1]
    nodelist = parser.parse(("endpalette_override",))
    parser.delete_first_token()
    
    return PaletteOverrideNode(block_name, nodelist)


# ========================
# PALETTE_BLOCK NODE
# ========================

class PaletteBlockNode(Node):
    """
    Represents a named slot (block) within a component.
    
    Structure:
        {% palette_block card_header %}
            ... default content ...
        {% endpalette_block %}
    
    Rendering behavior:
    1. Render the base content (self.nodelist)
    2. Check if an override exists in context.render_context["palette_overrides"]
    3. If override exists, create an isolated context with block.super
    4. Render override with access to all parent variables
    
    This matches Django's {% block %} / {{ block.super }} semantics.
    """

    def __init__(self, block_name, nodelist):
        self.block_name = block_name
        self.nodelist = nodelist

    def render(self, context):
        """Render the palette_block with override support."""
        # Render the base content
        original = self.nodelist.render(context)
        
        # Check for overrides (set by palette_ui before rendering component)
        overrides = context.render_context.get("palette_overrides", {}) or {}
        
        if self.block_name not in overrides:
            # No override; return base content
            return original
        
        # Override exists; render it with block.super available
        override_nodelist = overrides[self.block_name]
        
        class _Block:
            """Provides block.super access to the original rendered content."""
            def __init__(self, sup):
                self.super = sup
        
        # Build isolated context preserving parent variables
        base = context.flatten()
        temp_ctx = TempContext(base)
        temp_ctx["block"] = _Block(original)
        
        return override_nodelist.render(temp_ctx)


@register.tag("palette_block")
def palette_block(parser, token):
    """
    Parse a palette_block tag.
    
    Syntax:
        {% palette_block name %}...{% endpalette_block %}
    
    Note: NO output during parsing. Parsing only constructs the AST.
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError(
            "palette_block takes exactly one argument: the block name"
        )
    
    block_name = bits[1]
    nodelist = parser.parse(("endpalette_block",))
    parser.delete_first_token()
    
    return PaletteBlockNode(block_name, nodelist)


# ========================
# PALETTE_COMPONENT NODE
# ========================

class PaletteComponentNode(Node):
    """
    Represents a component definition.
    
    Structure:
        {% palette_component "card" %}
            {% palette_block card_header %}...{% endpalette_block %}
            {% palette_block card_body %}...{% endpalette_block %}
        {% endpalette_component %}
    
    The component's nodelist is registered into context.render_context
    during the first render pass for later lookup by palette_ui.
    
    When rendered directly (not via palette_ui), returns the default
    rendered output so component definition files can be previewed.
    """

    def __init__(self, file_key, component_name, nodelist):
        """
        Args:
            file_key: Template filename (e.g., 'palette/components/card.html')
            component_name: Component identifier (e.g., 'card')
            nodelist: AST node list (may contain palette_block nodes)
        """
        self.file_key = file_key
        self.component_name = component_name
        self.nodelist = nodelist

    def render(self, context):
        """
        1. Register component nodelist into PALETTE_COMPONENTS registry
        2. Render the default content (for preview)
        """
        # Register into render_context for later lookup
        registry = context.render_context.setdefault("PALETTE_COMPONENTS", {})
        file_components = registry.setdefault(self.file_key, {})
        file_components[self.component_name] = self.nodelist
        
        # print(f"[PALETTE_COMPONENT] Registered '{self.component_name}' in '{self.file_key}'")
        
        # Expose registry to templates for debugging
        context["PALETTE_COMPONENTS"] = registry
        
        # Render default content
        return self.nodelist.render(context)


@register.tag("palette_component")
def palette_component(parser, token):
    """
    Parse a palette_component tag.
    
    Syntax:
        {% palette_component "component_name" %}...{% endpalette_component %}
    
    The component_name is extracted from quotes or used as-is.
    File key is determined from parser.origin (template filename).
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError(
            "palette_component requires exactly one argument: the component name"
        )
    
    raw = bits[1]
    
    # Handle quoted strings
    if raw and raw[0] in ('"', "'") and raw[-1] == raw[0]:
        component_name = raw[1:-1]
    else:
        component_name = raw
    
    # Determine template file key
    file_key = (
        getattr(parser.origin, "template_name", None) or
        getattr(parser.origin, "name", None) or
        "<unknown>"
    )
    
    # Parse the component's nodelist (includes nested palette_block nodes)
    nodelist = parser.parse(("endpalette_component",))
    parser.delete_first_token()
    
    return PaletteComponentNode(file_key, component_name, nodelist)


# ========================
# PALETTE_UI NODE
# ========================

def _parse_quoted_value(val_str):
    """
    Parse a prop value which can be:
    1. "literal string" -> ("literal", "literal string")
    2. "{{ variable }}" -> ("template_expr", "variable")
    3. "{% template_tag %}" -> ("tag", "template_tag")
    4. bare_variable -> ("expression", "bare_variable")
    5. Mixed: "prefix {{ var }} suffix" -> ("template_expr", "prefix {{ var }} suffix")
    
    Returns tuple of (type, content):
    - type: "literal", "template_expr", "tag", or "expression"
    - content: the extracted/normalized content
    
    Crucially:
    - Only treat as template_expr if wrapped in {{ }}
    - Only treat as tag if wrapped in {% %}
    - Otherwise treat as literal (even if unquoted)
    """
    val_str = val_str.strip()
    
    if not val_str:
        return ("literal", "")
    
    # Case 1: Quoted string - extract the inner content
    if val_str[0] in ('"', "'"):
        quote_char = val_str[0]
        # Find the matching closing quote
        end_idx = val_str.rfind(quote_char)
        
        if end_idx > 0:  # Found closing quote
            inner = val_str[1:end_idx]
            
            # Check what's inside the quotes
            # 1a: "{{ variable }}" -> template expression
            if inner.startswith("{{") and inner.endswith("}}"):
                expr_content = inner[2:-2].strip()
                return ("template_expr", expr_content)
            
            # 1b: "{% template_tag %}" -> template tag
            elif inner.startswith("{%") and inner.endswith("%}"):
                return ("tag", inner)
            
            # 1c: Mixed content with {{ }}: "prefix {{ var }} suffix"
            elif "{{" in inner and "}}" in inner:
                return ("template_expr", inner)
            
            # 1d: Regular quoted literal (including strings with spaces)
            else:
                return ("literal", inner)
        else:
            # Mismatched quotes
            return ("literal", val_str)
    
    # Case 2: Unquoted value
    # Check for template expression: {{ ... }}
    if val_str.startswith("{{") and val_str.endswith("}}"):
        expr_content = val_str[2:-2].strip()
        return ("template_expr", expr_content)
    
    # Check for template tag: {% ... %}
    if val_str.startswith("{%") and val_str.endswith("%}"):
        return ("tag", val_str)
    
    # Check for mixed expression: "prefix {{ var }} suffix" without quotes
    if "{{" in val_str and "}}" in val_str:
        return ("template_expr", val_str)
    
    # Case 3: Bare variable or literal
    # Treat as "expression" - could be a variable reference (e.g., stats.total_users)
    # The parser will later decide if it's a valid variable reference or just a string
    return ("expression", val_str)


class PaletteUINode(Node):

    def __init__(self, reserved, props, nodelist):
        """
        Args:
            reserved: dict of file/component FilterExpression or string literals
            props: dict of variable name -> FilterExpression
            nodelist: inner nodes (contains palette_override tags)
        """
        self.reserved = reserved
        self.props = props
        self.nodelist = nodelist

    def _resolve_token(self, expr, context):
        """
        Safely resolve a FilterExpression to a value.
        
        Returns None if resolution fails.
        """
        if expr is None:
            return None
        try:
            return expr.resolve(context)
        except Exception:
            return None

    def _find_component_in_registry(self, registry, tpl_name, comp_name):
        """
        Attempt to locate a component in the registry using multiple fallback strategies.
        
        Returns the component nodelist if found, None otherwise.
        """
        # Strategy 1: Direct lookup
        comp_nodelist = registry.get(tpl_name, {}).get(comp_name)
        if comp_nodelist is not None:
            return comp_nodelist
        
        # Strategy 2: Template object name match
        try:
            template_obj = loader.get_template(tpl_name)
            tpl_obj_name = (
                getattr(template_obj, "name", None) or
                getattr(getattr(template_obj, "origin", None), "name", None)
            )
            if tpl_obj_name:
                comp_nodelist = registry.get(tpl_obj_name, {}).get(comp_name)
                if comp_nodelist is not None:
                    return comp_nodelist
        except Exception:
            pass
        
        # Strategy 3: Basename match
        basename = os.path.basename(tpl_name)
        for key in list(registry.keys()):
            if os.path.basename(key) == basename:
                comp_nodelist = registry.get(key, {}).get(comp_name)
                if comp_nodelist is not None:
                    return comp_nodelist
        
        # Strategy 4: Scan template AST for component definition
        try:
            template_obj = loader.get_template(tpl_name)
            root_nodelist = (
                getattr(template_obj, "nodelist", None) or
                (hasattr(template_obj, "template") and
                 getattr(template_obj.template, "nodelist", None))
            )
            if root_nodelist:
                for node in _iter_nodelist_recursive(root_nodelist):
                    if (isinstance(node, PaletteComponentNode) and
                        node.component_name == comp_name):
                        # Register for future lookups
                        registry.setdefault(tpl_name, {})[comp_name] = node.nodelist
                        return node.nodelist
        except Exception:
            pass
        
        return None

    def render(self, context):
        """
        Render the palette_ui component with context variables and overrides.
        
        Process:
        1. Resolve file path and component name from expressions/literals
        2. Load template and trigger component registration if needed
        3. Resolve all context variables passed via 'with' clause
        4. Collect overrides from inner palette_override nodes
        5. Push context layer with component props
        6. Set overrides in render_context
        7. Render component nodelist
        8. Pop context and restore previous state
        """
        # Resolve file and component names
        file_expr = self.reserved.get("file")
        comp_expr = self.reserved.get("component")
        
        if file_expr is None or comp_expr is None:
            print("[PALETTE_UI] ERROR: Missing file or component expression")
            return ""
        
        # Resolve file path: can be string literal or FilterExpression ({{ var }})
        tpl_name = self._resolve_token(file_expr, context)
        if isinstance(file_expr, str):  # literal string
            tpl_name = file_expr
        
        # Resolve component name: can be string literal or FilterExpression ({{ var }})
        if isinstance(comp_expr, str):  # literal string
            comp_name = comp_expr
        else:
            comp_name = self._resolve_token(comp_expr, context)
        
        if not tpl_name or not comp_name:
            print(f"[PALETTE_UI] ERROR: Invalid file='{tpl_name}' or component='{comp_name}'")
            return f"<!-- palette_ui: file='{tpl_name}' component='{comp_name}' -->"
        
        # Get or create component registry
        registry = context.render_context.setdefault("PALETTE_COMPONENTS", {})
        
        # Ensure template is loaded, which will trigger component registration
        try:
            template_obj = loader.get_template(tpl_name)
        except Exception as e:
            print(f"[PALETTE_UI] ERROR: Could not load template '{tpl_name}': {e}")
            return f"<!-- palette_ui: template '{tpl_name}' not found -->"
        
        # Locate component nodelist in registry
        comp_nodelist = self._find_component_in_registry(registry, tpl_name, comp_name)
        
        if comp_nodelist is None:
            print(f"[PALETTE_UI] ERROR: Component '{comp_name}' not found in '{tpl_name}'")
            return f"<!-- palette_ui: component '{comp_name}' not found -->"
        
        # Resolve context variables from 'with' clause
        # Each value is either:
        # - ("literal", string_value) -> use as-is
        # - ("expression", FilterExpression) -> resolve from context
        # - ("tag", template_tag_str) -> would need special handling
        local_vars = {}
        for var_name, var_spec in self.props.items():
            try:
                if isinstance(var_spec, tuple) and len(var_spec) == 2:
                    var_type, var_value = var_spec
                    if var_type == "literal":
                        local_vars[var_name] = var_value
                    elif var_type == "expression":
                        resolved_value = var_value.resolve(context)
                        local_vars[var_name] = resolved_value
                    elif var_type == "tag":
                        local_vars[var_name] = var_value
                    else:
                        local_vars[var_name] = None
                else:
                    # Fallback: assume it's a FilterExpression for backward compatibility
                    resolved_value = var_spec.resolve(context)
                    local_vars[var_name] = resolved_value
            except Exception as e:
                print(f"[PALETTE_UI] WARNING: Could not resolve {var_name}: {e}")
                local_vars[var_name] = None
        
        # Collect overrides from inner palette_override nodes
        overrides = {}
        for node in _iter_nodelist_recursive(self.nodelist):
            if isinstance(node, PaletteOverrideNode):
                # Strip quotes from override block name if needed
                block_name = node.name
                if block_name and block_name[0] in ('"', "'") and block_name[-1] == block_name[0]:
                    block_name = block_name[1:-1]
                overrides[block_name] = node.nodelist
        
        print(f"[PALETTE_UI] Rendering component='{comp_name}' from file='{tpl_name}'")
        
        # Save previous state (for nested palette_ui calls)
        prev_overrides = context.render_context.get("palette_overrides", None)
        prev_components = context.render_context.get("palette_current_component", None)
        
        # Set up render_context for palette_block nodes to access
        context.render_context["palette_overrides"] = overrides
        context.render_context["palette_current_component"] = comp_name
        
        # Push a new context layer for component props (matches Django's {% include %} tag)
        context.push()
        try:
            # Inject component props into the new context layer
            for var_name, var_value in local_vars.items():
                context[var_name] = var_value
            
            # Expose registry for debugging
            context["PALETTE_COMPONENTS"] = registry
            context["component_name"] = comp_name
            
            # Render the component nodelist with new context and overrides
            rendered = comp_nodelist.render(context)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            rendered = f"<!-- palette_ui render error: {e} -->"
        finally:
            # Pop the context layer
            context.pop()
            
            # Restore previous state
            context.render_context["palette_overrides"] = prev_overrides
            context.render_context["palette_current_component"] = prev_components
                    
        return mark_safe(rendered)


@register.tag("palette_ui")
def do_palette_ui(parser, token):
    """
    Parse a palette_ui tag.
    
    Grammar:
      {% palette_ui file="path/to/components.html" component="card_name" with title=page.title count=total %}
         {% palette_override card_header %}
            <h2>{{ title }}</h2>
         {% endpalette_override %}
      {% endpalette_ui %}
    
    Supports:
    - file="..." or file=variable_name for template path
    - component="..." or component=variable_name for component name
    - with key1=value1 key2=value2 ... for context variables
      - value can be: "literal_string", "{{ variable }}", "{% url ... %}", variable_name
    - Inner palette_override blocks for slot overrides
    """
    bits = token.split_contents()
    tag_name = bits[0]
    
    if len(bits) < 3:
        raise TemplateSyntaxError(
            f"{tag_name} requires at least 'file=' and 'component=' keyword arguments. "
            f"Syntax: {{% {tag_name} file=\"path\" component=\"name\" [with key=value ...] %}}"
        )
    
    # Parse keyword arguments
    file_expr = None
    comp_expr = None
    with_vars = {}
    
    i = 1
    while i < len(bits):
        bit = bits[i]
        
        # Stop at 'with' keyword
        if bit == "with":
            i += 1
            break
        
        # Must be a keyword argument (key=value)
        if "=" not in bit:
            raise TemplateSyntaxError(
                f"{tag_name}: Expected keyword argument (key=value), got '{bit}'"
            )
        
        key, val = bit.split("=", 1)
        
        # Parse the value
        val_type, val_content = _parse_quoted_value(val)
        
        # Handle reserved keywords
        if key == "file":
            if val_type == "literal":
                # Literal path
                file_expr = val_content
            elif val_type == "template_expr":
                # Template expression: compile as filter
                file_expr = parser.compile_filter(val_content)
            elif val_type == "tag":
                # Template tag - compile
                file_expr = parser.compile_filter(val_content)
            else:  # "expression"
                # Bare variable
                file_expr = parser.compile_filter(val_content)
        
        elif key == "component":
            if val_type == "literal":
                comp_expr = val_content
            elif val_type == "template_expr":
                comp_expr = parser.compile_filter(val_content)
            elif val_type == "tag":
                comp_expr = parser.compile_filter(val_content)
            else:  # "expression"
                comp_expr = parser.compile_filter(val_content)
        
        else:
            # Treat as a 'with' variable before 'with' keyword is seen
            if val_type == "literal":
                # Literal value - store as-is, will be used as string
                with_vars[key] = ("literal", val_content)
            elif val_type == "template_expr":
                # Template expression - compile as filter
                with_vars[key] = ("expression", parser.compile_filter(val_content))
            elif val_type == "tag":
                # Template tag - we'll handle this specially
                with_vars[key] = ("tag", val_content)
            else:  # "expression"
                # Bare variable reference - compile as filter
                with_vars[key] = ("expression", parser.compile_filter(val_content))
        
        i += 1
    
    # Parse remaining 'with' variables
    while i < len(bits):
        bit = bits[i]
        if "=" not in bit:
            raise TemplateSyntaxError(
                f"{tag_name}: Expected 'key=value' in with clause, got '{bit}'"
            )
        
        key, val = bit.split("=", 1)
        val_type, val_content = _parse_quoted_value(val)
        
        if val_type == "literal":
            with_vars[key] = ("literal", val_content)
        elif val_type == "template_expr":
            with_vars[key] = ("expression", parser.compile_filter(val_content))
        elif val_type == "tag":
            with_vars[key] = ("tag", val_content)
        else:  # "expression"
            with_vars[key] = ("expression", parser.compile_filter(val_content))
        i += 1
    
    # Validate required arguments
    if file_expr is None:
        raise TemplateSyntaxError(f"{tag_name} requires 'file=' argument")
    if comp_expr is None:
        raise TemplateSyntaxError(f"{tag_name} requires 'component=' argument")
    
    # Parse inner content (palette_override blocks)
    inner_nodelist = parser.parse(("endpalette_ui",))
    parser.delete_first_token()
    
    # Store reserved keywords (file, component) separately from props
    reserved = {
        "file": file_expr,
        "component": comp_expr,
    }
    
    # print(f"[PALETTE_UI PARSER] Parsed tag with file={file_expr!r}, component={comp_expr!r}")
    # print(f"[PALETTE_UI PARSER] With vars: {list(with_vars.keys())}")
    
    return PaletteUINode(reserved, with_vars, inner_nodelist)



# ========================
# UTILITY TAGS & FILTERS
# ========================

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
    return reverse('palette_admin:index')


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
    print("Widget for field:", field.field.widget_type)
    return field.field.widget_type


@register.filter
def is_multiple_select(field):
    from django.forms.models import ModelMultipleChoiceField
    if isinstance(field.field.field, ModelMultipleChoiceField):
        return True
    return False


@register.filter(name='admin_fields')
def admin_fields(obj):
    """
    Returns a list of (field_name, field_value) tuples for an object.
    Useful for displaying object details in admin interfaces.
    
    Example:
        {% for field_name, field_value in obj|admin_fields %}
            <span>{{ field_name }}: {{ field_value }}</span>
        {% endfor %}
    """
    from django.contrib.admin.utils import label_for_field
    from django.db import models
    
    if not obj:
        return []
    
    result = []
    model = obj.__class__
    
    # Get all fields from the model
    for field in model._meta.get_fields():
        # Skip many-to-many and reverse relations
        if field.many_to_one or field.one_to_one:
            try:
                value = getattr(obj, field.name, None)
                result.append((field.verbose_name.title(), value))
            except Exception:
                pass
        elif not (field.many_to_many or field.one_to_many):
            try:
                value = getattr(obj, field.name, None)
                result.append((field.verbose_name.title(), value))
            except Exception:
                pass
    
    return result


@register.filter(name='admin_field')
def admin_field(obj, field_name):
    """
    Get a specific field value from an object.
    
    Example:
        {{ obj|admin_field:"email" }}
    """
    try:
        return getattr(obj, field_name, None)
    except Exception:
        return None


@register.filter(name='humanize_name')
def humanize_name(value):
    """
    Convert snake_case or underscored names to Title Case.
    
    Example:
        {{ "first_name"|humanize_name }} -> "First Name"
        {{ "email_address"|humanize_name }} -> "Email Address"
    """
    if not value:
        return value
    return ' '.join(word.capitalize() for word in str(value).replace('_', ' ').split())


@register.filter(name='format_field_value')
def format_field_value(value, field_name=''):
    """
    Format field values based on their type and content.
    Returns appropriate formatting for booleans, dates, datetimes, etc.
    
    Example:
        {{ item|getattr:"is_active"|format_field_value }}
    """
    from django.utils.html import format_html
    from datetime import date, datetime
    
    # Handle None/null values
    if value is None or value == '':
        return mark_safe('<span class="text-muted">—</span>')
    
    # Handle boolean values
    if isinstance(value, bool):
        if value:
            return mark_safe('<i class="bi bi-check-circle-fill" style="color: #28a745; font-size: 1.2em;"></i>')
        else:
            return mark_safe('<i class="bi bi-x-circle-fill" style="color: #dc3545; font-size: 1.2em;"></i>')
    
    # Handle datetime objects
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M')
    
    # Handle date objects
    if isinstance(value, date):
        return value.strftime('%Y-%m-%d')
    
    # Handle other types - convert to string
    return str(value)










