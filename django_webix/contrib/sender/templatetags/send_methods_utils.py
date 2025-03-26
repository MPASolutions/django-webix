from django import template
from django.conf import settings
from django_webix.contrib.sender.utils import user_can_send as check_user_can_send

register = template.Library()

CONF = getattr(settings, "WEBIX_SENDER", None)


@register.simple_tag(takes_context=True)
def user_can_send(context):
    """Returns boolean to indicate if user has send permission"""

    request = context["request"]
    return check_user_can_send(user=request.user)


@register.simple_tag(takes_context=True)
def is_list_available(context):
    """Returns boolean to indicate if there are lists configured"""

    for send_method in CONF["send_methods"]:
        if send_method["show_in_list"] is True:
            return True
    return False


@register.simple_tag(takes_context=True)
def is_chat_available(context):
    """Returns boolean to indicate if there are chats configured"""

    for send_method in CONF["send_methods"]:
        if send_method["show_in_chat"] is True:
            return True
    return False
