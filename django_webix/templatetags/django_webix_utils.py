# -*- coding: utf-8 -*-

import datetime
import re

import six
from django import template
from django.apps import apps
from django.conf import settings
from django.template import TemplateSyntaxError
from django.utils.timezone import is_naive, make_naive

try:
    from django.template.base import TokenType
except ImportError:
    # Django < 2.1
    from django.template.base import TOKEN_BLOCK
else:
    TOKEN_BLOCK = TokenType.BLOCK

from django.template.defaulttags import (CommentNode, IfNode, LoadNode,
                                         find_library, load_from_library)
from django.template.smartif import Literal

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


@register.tag
def friendly_load(parser, token):
    """
    Tries to load a custom template tag set. Non existing tag libraries
    are ignored.
    This means that, if used in conjunction with ``if_has_tag``, you can try to
    load the comments template tag library to enable comments even if the
    comments framework is not installed.
    For example::
        {% load friendly_loader %}
        {% friendly_load comments webdesign %}
        {% if_has_tag render_comment_list %}
            {% render_comment_list for obj %}
        {% else %}
            {% if_has_tag lorem %}
                {% lorem %}
            {% endif_has_tag %}
        {% endif_has_tag %}
    """
    bits = token.contents.split()
    if len(bits) >= 4 and bits[-2] == "from":
        # from syntax is used; load individual tags from the library
        name = bits[-1]
        try:
            lib = find_library(parser, name)
            subset = load_from_library(lib, name, bits[1:-2])
            parser.add_library(subset)
        except TemplateSyntaxError:
            pass
    else:
        # one or more libraries are specified; load and add them to the parser
        for name in bits[1:]:
            try:
                lib = find_library(parser, name)
                parser.add_library(lib)
            except TemplateSyntaxError:
                pass
    return LoadNode()


def do_if_has_tag(parser, token, negate=False):
    """
    The logic for both ``{% if_has_tag %}`` and ``{% if not_has_tag %}``.
    Checks if all the given tags exist (or not exist if ``negate`` is ``True``)
    and then only parses the branch that will not error due to non-existing
    tags.
    This means that the following is essentially the same as a
    ``{% comment %}`` tag::
      {% if_has_tag non_existing_tag %}
          {% non_existing_tag %}
      {% endif_has_tag %}
    Another example is checking a built-in tag. This will always render the
    current year and never FAIL::
      {% if_has_tag now %}
          {% now "Y" %}
      {% else %}
          FAIL
      {% endif_has_tag %}
    """
    bits = list(token.split_contents())
    if len(bits) < 2:
        raise TemplateSyntaxError("%r takes at least one arguments" % bits[0])
    end_tag = 'end%s' % bits[0]
    has_tag = all([tag in parser.tags for tag in bits[1:]])
    has_tag = (not negate and has_tag) or (negate and not has_tag)
    nodelist_true = nodelist_false = CommentNode()
    if has_tag:
        nodelist_true = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else':
            parser.skip_past(end_tag)
    else:
        while parser.tokens:
            token = parser.next_token()
            if token.token_type == TOKEN_BLOCK and token.contents == end_tag:
                return IfNode([
                    (Literal(has_tag), nodelist_true),
                    (None, nodelist_false)
                ])
            elif token.token_type == TOKEN_BLOCK and token.contents == 'else':
                break
        nodelist_false = parser.parse((end_tag,))
        parser.next_token()
    return IfNode([(Literal(has_tag), nodelist_true),
                   (None, nodelist_false)])


@register.tag
def if_has_tag(parser, token):
    """
    Do something if all given tags are loaded::
       {% load friendly_loader %}
       {% friendly_load webdesign %}
       {% if_has_tag lorem %}
            {% lorem %}
       {% else %}
            Non dummy content goes here!
       {% endif_has_tag %}
    When given multiple arguments each and every tag in the list has to be
    available. This means that the following will render nothing::
       {% if_has_tag now nonexisting_tag %}
           {% now "Y" %}
       {% endif_has_tag %}
    """
    return do_if_has_tag(parser, token)


@register.tag
def ifnot_has_tag(parser, token):
    """
    Do something unless any given tag is loaded::
       {% load friendly_loader %}
       {% friendly_load comments %}
       {% ifnot_has_tag render_comment_list %}
            Comment support has been disabled.
       {% else %}
            {% render_comment_list for obj %}
       {% endifnot_has_tag %}
    In the case of multiple arguments, the condition will trigger if any tag in
    the list is unavailable. This means that the following will still render
    the current year::
       {% ifnot_has_tag now nonexisting_tag %}
           {% now "Y" %}
       {% endifnot_has_tag %}
    """
    return do_if_has_tag(parser, token, True)
