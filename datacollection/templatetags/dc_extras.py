from django.template.defaultfilters import stringfilter
from django import template

import settings

register = template.Library()

@register.filter
@stringfilter
def split(value, arg):
    return value.split(arg)

@register.filter
@stringfilter
def sub_site(value):
    return settings.SUB_SITE + value
