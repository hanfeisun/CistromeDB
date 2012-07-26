from django.template.defaultfilters import stringfilter
from django import template
from django.core.urlresolvers import reverse

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

@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr)

@register.filter
@stringfilter
def my_reverse(view_name, args):
    return reverse(view_name, args=[args])

@register.filter
def is_in(obj, lst):
    """replicates the 'in' built-in operator in python"""
    return obj in lst

@register.filter
@stringfilter
def get_fname(s):
    """expects file paths to be: zzz/xxx/filename.yyy
    returns filename.yyy
    """
    return s.split("/")[-1]
