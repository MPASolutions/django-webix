from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from django_webix.contrib.admin.forms import WebixAdminMenuForm
from django_webix.contrib.admin.models import WebixAdminMenu


def menu_dwadmin_register(site):
    from mptt.admin import DraggableMPTTAdmin

    @admin.register(WebixAdminMenu)
    class MenuAdmin(DraggableMPTTAdmin):
        form = WebixAdminMenuForm
        raw_id_fields = ('parent',)
        search_fields = ('label', 'url', 'model__model')
        filter_horizontal = ['groups']
        list_filter = ('enabled', 'active_all', 'model')
        list_per_page = 1000
        expand_tree_by_default = True
        mptt_level_indent = 30
        list_display = ('tree_actions', 'indented_title', 'label', 'enabled', 'active_all', 'model', 'prefix', 'get_groups_string')
        list_display_links = (
            'indented_title',
        )
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
