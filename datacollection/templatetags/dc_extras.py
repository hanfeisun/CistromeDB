from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()

@register.filter
@stringfilter
def split(value, arg):
    return value.split(arg)
