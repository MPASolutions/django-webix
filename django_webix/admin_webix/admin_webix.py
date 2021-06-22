# -*- coding: utf-8 -*-
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import F
from django.urls import path

from django_webix import admin_webix as admin
from django_webix.admin_webix.forms import GroupAdminForm, AdminPasswordChangeForm
from django_webix.admin_webix.views import UserAdminCreate, UserAdminUpdate
from django_webix.views.generic.actions import multiple_delete_action



class UserAdmin(admin.ModelWebixAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(userid=F('id'))
        return qs

    list_display = [
        {
            'field_name': 'username',
            'datalist_column': '''{
                id: "username",
                header: ["Utente", {content: "serverFilter" }],
                fillspace:true,
                sort: "server",
                serverFilterType: "icontains",
                }'''
        },
        {
            'field_name': 'email',
            'datalist_column': '''{
                id: "email",
                header: ["Indirizzo email", {content: "serverFilter" }],
                adjust:"all",
                sort: "server",
                serverFilterType: "icontains",
                }'''
        },
        {
            'field_name': 'first_name',
            'datalist_column': '''{
                id: "first_name",
                header: ["Nome", {content: "serverFilter" }],
                adjust:"all",
                sort: "server",
                serverFilterType: "icontains",
                }'''
        },
        {
            'field_name': 'last_name',
            'datalist_column': '''{
                id: "last_name",
                header: ["Cognome", {content: "serverFilter" }],
                adjust:"all",
                sort: "server",
                serverFilterType: "icontains",
                }'''
        },
        {
            'field_name': 'is_staff',
            'datalist_column': '''{
                id: "is_staff",
                header: ["Staff", {content: "serverSelectFilter" , options:[{id: 'True', value: 'Sì'}, {id: 'False', value: 'No'}] }],
                adjust:"all",
                sort: "server",
                serverFilterType: "",
                template:custom_checkbox_yesnonone,
                }'''
        },
        {
            'field_name': 'is_superuser',
            'datalist_column': '''{
                id: "is_superuser",
                header: ["Superutente", {content: "serverSelectFilter" , options:[{id: 'True', value: 'Sì'}, {id: 'False', value: 'No'}] }],
                adjust:"all",
                sort: "server",
                serverFilterType: "",
                 template:custom_checkbox_yesnonone,
                }'''
        },
        {
            'field_name': 'is_active',
            'datalist_column': '''{
                id: "is_active",
                header: ["Attivo", {content: "serverSelectFilter" , options:[{id: 'True', value: 'Sì'}, {id: 'False', value: 'No'}] }],
                adjust:"all",
                sort: "server",
                serverFilterType: "",
                template:custom_checkbox_yesnonone,
                }'''
        },
        {
            'field_name': 'groups__name',
            'datalist_column': '''{
                id: "groups__name",
                serverFilterType:"icontains",
                adjust:"all",
                header: ["Gruppi", {content: "serverFilter"}],
                sort: "server"
                }'''
        },
        ]
    def get_list_display(self, request=None):
        if apps.is_installed("hijack") and request.user.is_superuser:
            return self.list_display + [{
                'field_name': 'userid',
                'click_action': '''document.location.href="/hijack/"+el['id'];''',
                'datalist_column': '''{
                id: "userid",
                header: ['',''],
                adjust: "data",
                template: 'Hijack'
                }'''
            }]
        else:
            return self.list_display

    enable_json_loading = True
    only_superuser = True
    # form = UserAdminForm
    create_view = UserAdminCreate
    update_view = UserAdminUpdate
    actions = [multiple_delete_action]

    def get_urls(self):
        return [
            path(
                '<int:pk>/password/admin',
                self.user_change_password().as_view(),
                name='admin_webix_password_change_admin',
            ),
        ] + super().get_urls()

    def user_change_password(self):
        _admin = self

        from django_webix.views import WebixUpdateView

        class WebixAdminUpdateView(WebixUpdateView):
            url_pattern_update = 'admin_webix:admin_webix_password_change_admin'
            url_pattern_list = 'admin_webix:users.user.list'
            form_class = AdminPasswordChangeForm
            model = _admin.model
            # form_class = _admin.get_form_create_update()

            inlines = _admin.inlines
            model_copy_fields = _admin.get_form_fields()
            enable_button_save_continue = False
            enable_button_save_addanother = False
            enable_button_save_gotolist = _admin.enable_button_save_gotolist

            def get_queryset(self):
                return _admin.get_queryset(self.request)

        return WebixAdminUpdateView

admin.site.register(get_user_model(), admin_class=UserAdmin)


class GroupAdmin(admin.ModelWebixAdmin):
    list_display = ['name']
    enable_json_loading = True
    only_superuser = True
    form = GroupAdminForm

admin.site.register(Group, admin_class=GroupAdmin)

