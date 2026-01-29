from django import template
from django.template.defaultfilters import linebreaksbr
from django.utils.safestring import SafeString

register = template.Library()

@register.filter
def changelog(value: str) -> SafeString:
    return linebreaksbr(value.replace('; ', '\n'))
