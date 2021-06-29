# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from feincms.admin import tree_editor

from django_webix.admin_webix.forms import WebixAdminMenuForm
from django_webix.admin_webix.models import WebixAdminMenu


def menu_admin_webix_register(site):
    @admin.register(WebixAdminMenu)
    class MenuAdmin(tree_editor.TreeEditor):
        form = WebixAdminMenuForm
        raw_id_fields = ('parent',)
        search_fields = ('label', 'url', 'model__model')
        filter_horizontal = ['groups']
        list_filter = ('enabled', 'active_all', 'model')
        list_per_page = 1000
        list_display = ('id', 'label', 'enabled', 'active_all', 'model', 'prefix', 'get_groups_string')
        fieldsets = (
            ('Details', {
                'fields': (
                    ('parent'),
                    ('label', 'icon'),
                    ('url', 'prefix'),
                    ('model'),
                    ('enabled', 'active_all'),
                    ('groups'),
                ),
            }),
        )

        def get_groups_string(self, item):
            return mark_safe(', '.join([g[1] for g in item.groups.values_list()]))

        get_groups_string.short_description = _('Groups')

        def get_form(self, request, obj=None, change=False, **kwargs):
            form = super().get_form(request, obj, change, **kwargs)
            _models = list(set([model for (model, prefix), model_admin in site._registry.items()]))
            qs = ContentType.objects.all()
            for el in qs:
                if el.model_class() not in _models:
                    qs = qs.exclude(pk=el.pk)
            form.base_fields['model'].queryset = qs
            return form