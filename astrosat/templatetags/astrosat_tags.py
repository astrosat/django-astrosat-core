from django import template
from django.utils.html import mark_safe

import astrosat


register = template.Library()

##################
# some constants #
##################

@register.simple_tag
def astrosat_title():
    return mark_safe(astrosat.__title__)


@register.simple_tag
def astrosat_author():
    return mark_safe(astrosat.__author__)


@register.simple_tag
def astrosat_version():
    return mark_safe(astrosat.__version__)


#####################
# some useful utils #
#####################

@register.filter
def get_value(dictionary, key):
    """
    Returns the value of the dictionary item w/ a given key.
    Returns None if the key is not in the dictionary.
    """
    # Ridiculous that this is not built into Django!
    return dictionary.get(key)


@register.filter
def get_key(dictionary, value):
    """
    Returns the key of the 1st time in dictionary w/ a given value.
    Returns None if the value is not in the dictionary.
    """
    for k, v in dictionary.items():
        if v == value:
            return k
    return None
