from django import template
from django.template.loader import render_to_string, get_template
from django.template.base import token_kwargs
from django.template.defaultfilters import stringfilter
from django.template import engines
from django.template.context import Context
from django.utils.safestring import mark_safe
from django.urls import reverse
import re

register = template.Library()

# @template.defaultfilters.stringfilter
# @template.library.
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

@register.tag(name="palette_ui")
def do_palette_ui(parser, token):
    bits = token.split_contents()
    tag_name = bits[0]

    if len(bits) < 2:
        raise template.TemplateSyntaxError(f"{tag_name} requires at least the template path.")

    template_path = parser.compile_filter(bits[1])
    context_vars = {}

    if len(bits) >= 3 and bits[2] == "with":
        context_vars = token_kwargs(bits[3:], parser, support_legacy=False)

    # Look ahead to determine if the tag is a block or inline
    token_list = list(parser.tokens)
    if token_list and token_list[0].contents == "endpalette_ui":
        # Inline tag (next token is end)
        parser.delete_first_token()
        return PaletteUI(template_path, context_vars, None)

    # Otherwise, parse as a block tag
    nodelist = parser.parse(('endpalette_ui',))
    parser.delete_first_token()  # remove 'endpalette_ui'
    return PaletteUI(template_path, context_vars, nodelist)


class PaletteUI(template.Node):
    def __init__(self, template_path, context_vars, nodelist=None):
        self.template_path = template_path
        self.context_vars = context_vars
        self.nodelist = nodelist

    def render_template_string(self, template_string, context):
        engine = engines['django']
        tmpl = engine.from_string(template_string)
        return tmpl.render(context.flatten())

    def render(self, context):
        template_path = self.template_path.resolve(context)
        template_obj = get_template(template_path)

        base_context = context.flatten()

        # Render and resolve variables
        extra_context = {}
        for key, val in self.context_vars.items():
            resolved = val.resolve(context)
            if isinstance(resolved, str) and ("{{" in resolved or "{%" in resolved):
                rendered = self.render_template_string(resolved, context)
                extra_context[key] = mark_safe(rendered)
            else:
                extra_context[key] = mark_safe(resolved)

        combined_context = {**base_context, **extra_context}
        rendered_component = template_obj.render(combined_context)

        # If no block content, just return the rendered component
        if not self.nodelist:
            return mark_safe(rendered_component)

        # Else render block with palette_ui.super
        context.push()
        context['palette_ui'] = {'super': mark_safe(rendered_component)}
        rendered_block = self.nodelist.render(context)
        context.pop()
        return mark_safe(rendered_block)


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


