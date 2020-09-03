# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import six
from django import template
from django.conf import settings
from django.utils.timezone import is_naive, make_naive
import datetime
from django.apps import apps

register = template.Library()


@register.filter('get_value_from_dict')
def get_value_from_dict(dict_data, key):
    """
    usage example {{ your_dict|get_value_from_dict:your_key }}
    """
    if key:
        return dict_data.get(key)


@register.simple_tag(name='webix_version')
def webix_version():
    return settings.WEBIX_VERSION


@register.simple_tag(name='webix_license')
def webix_license():
    return settings.WEBIX_LICENSE


@register.simple_tag(name='is_installed_djangowebixleaflet')
def is_installed_djangowebixleaflet():
    return apps.is_installed("django_webix_leaflet")


@register.simple_tag(name='is_installed_djangowebixfilter')
def is_installed_djangowebixfilter():
    return apps.is_installed("webix_filter")


@register.simple_tag(name='webix_history_enable')
def webix_history_enable():
    if hasattr(settings, 'WEBIX_HISTORY_ENABLE'):
        return settings.WEBIX_HISTORY_ENABLE
    else:
        return False


@register.simple_tag(name='webix_fontawesome_css_url')
def webix_fontawesome_css_url():
    if hasattr(settings, 'WEBIX_FONTAWESOME_CSS_URL'):
        return settings.WEBIX_FONTAWESOME_CSS_URL
    else:
        return 'django_webix/fontawesome-5.7.2/css/all.min.css'


@register.simple_tag(name='webix_fontawesome_version')
def webix_fontawesome_version():
    if hasattr(settings, 'WEBIX_FONTAWESOME_VERSION'):
        return settings.WEBIX_FONTAWESOME_VERSION
    else:
        return '5.7.2'


@register.filter
def comma_to_underscore(value):
    return value.replace(".", "_")


@register.filter_function
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)


@register.filter
def format_list_value(value):
    if type(value) == datetime.date:
        return value.strftime('%d/%m/%Y')
    elif type(value) == datetime.datetime:
        if not is_naive(value):
            value = make_naive(value)
        return value.strftime('%d/%m/%Y %H:%M')
    elif value is None:
        return ''
    return str(value)


@register.filter
def getattr(obj, args):
    """ Try to get an attribute from an object.

    Example: {% if block|getattr:"editable,True" %}

    Beware that the default is always a string, if you want this
    to return False, pass an empty second argument:
    {% if block|getattr:"editable," %}
    """
    splitargs = args.split(',')
    try:
        (attribute, default) = splitargs
    except ValueError:
        (attribute, default) = args, ''

    if isinstance(obj, six.string_types):
        return obj

    try:
        attr = obj.__getattribute__(attribute)
    except AttributeError:
        attr = obj.__dict__.get(attribute, default)
    except Exception:
        attr = default

    if hasattr(attr, '__call__'):
        return attr.__call__()
    else:
        return attr


class SetVarNode(template.Node):
    def __init__(self, new_val, var_name):
        self.new_val = new_val
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = self.new_val
        return ''


@register.tag
def setvar(parser, token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    new_val, var_name = m.groups()
    if not (new_val[0] == new_val[-1] and new_val[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return SetVarNode(new_val[1:-1], var_name)
