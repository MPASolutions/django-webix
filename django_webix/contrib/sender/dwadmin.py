from django.utils.html import escapejs
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from django_webix.contrib import admin
from django_webix.contrib.sender.models import MessageTypology, MessageTypologiesGroup


# @admin.register(MessageTypology, site=site)
class MessageTypologyAdmin(admin.ModelWebixAdmin):
    order_by = ['typology']

    list_display = [
        {
            'field_name': 'typology',
            'datalist_column': format_lazy(
                '''{{
                id: "typology",
                serverFilterType:"icontains",
                header: ["{}", {{content: "serverFilter"}}],
                fillspace: true,
                sort: "server"
                }}''',
                escapejs(_("Typology")))
        }
    ]

class MessageTypologiesGroupAdmin(admin.ModelWebixAdmin):
    order_by = ['group_typologies']

    list_display = [
        {
            'field_name': 'group_typologies',
            'datalist_column': format_lazy(
                '''{{
                id: "group_typologies",
                serverFilterType:"icontains",
                header: ["{}", {{content: "serverFilter"}}],
                fillspace: true,
                sort: "server"
                }}''',
                escapejs(_("Group typologies")))
        }
    ]
