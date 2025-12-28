from django import template
from django.utils.safestring import SafeString, mark_safe

register = template.Library()

@register.filter
def changelog(value: str) -> SafeString:
    return mark_safe(value.replace('; ', '<br/ >'))
