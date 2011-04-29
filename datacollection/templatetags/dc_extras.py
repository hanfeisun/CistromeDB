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
    if settings.SUB_SITE:
        tmp = ""
        if not settings.SUB_SITE.startswith("/"):
            #prepend /
            tmp = "/"
        tmp = tmp + settings.SUB_SITE
        if tmp.endswith("/"):
            #drop / at end
            tmp = tmp[:-1]
        return tmp + value
    else:
        return value
