from django import template
from django.utils.safestring import SafeString, mark_safe

register = template.Library()

@register.filter
def fa_checkbox(value: bool) -> SafeString:
    if value:
        return mark_safe('<span class="fa-fw fa-regular fa-square-check"></span>')
    return mark_safe('<span class="fa-fw fa-regular fa-square"></span>')
