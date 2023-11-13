from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import F
from django.urls import path
from django.utils.html import escapejs
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from django_webix.contrib import admin
from django_webix.contrib.admin.forms import GroupAdminForm, AdminPasswordChangeForm
from django_webix.contrib.admin.forms import UserAdminUpdateForm, UserAdminCreateForm
from django_webix.views.generic.actions import multiple_delete_action


class UserAdmin(admin.ModelWebixAdmin):
    def has_add_permission(self, view, request):
        if request.user.is_superuser:
            return super().has_add_permission(view, request)
        return False

    def has_change_permission(self, view, request, obj=None):
        if request.user.is_superuser:
            return super().has_change_permission(view, request, obj)
        return False

    def has_delete_permission(self, view, request, obj=None):
        if request.user.is_superuser:
            return super().has_delete_permission(view, request, obj)
        return False

    def has_view_permission(self, view, request, obj=None):
        if request.user.is_superuser:
            return super().has_view_permission(view, request, obj)
        return False

    def get_queryset(self, view=None, request=None):
        qs = super().get_queryset(request)
        qs = qs.annotate(userid=F('id'))
        return qs

    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active',
                    'groups__name']
    list_display_mobile = ['first_name', 'last_name', 'is_active', 'is_superuser']
    list_display_header = {
        'username': {
            'field_name': 'username',
            'datalist_column': format_lazy('''{{
                id: "username",
                header: ["{}", {{content: "serverFilter" }}],
                fillspace:true,
                sort: "server",
                serverFilterType: "icontains",
            }}''',
            escapejs(_("User")))
        },
        'email': {
            'field_name': 'email',
            'datalist_column': format_lazy('''{{
                id: "email",
                header: ["{}", {{content: "serverFilter" }}],
                adjust:"all",
                sort: "server",
                serverFilterType: "icontains",
            }}''',
            escapejs(_("Email")))
        },
        'first_name': {
            'field_name': 'first_name',
            'datalist_column': format_lazy('''{{
                id: "first_name",
                header: ["{}", {{content: "serverFilter" }}],
                adjust:"all",
                sort: "server",
                serverFilterType: "icontains",
            }}''',
            escapejs(_("Name")))
        },
        'last_name': {
            'field_name': 'last_name',
            'datalist_column': format_lazy('''{{
                id: "last_name",
                header: ["{}", {{content: "serverFilter" }}],
                adjust:"all",
                sort: "server",
                serverFilterType: "icontains",
            }}''',
            escapejs(_("Surname")))
        },
        'is_staff': {
            'field_name': 'is_staff',
            'datalist_column': format_lazy('''{{
                id: "is_staff",
                header: ["{}", {{content: "serverSelectFilter" ,
                        options:[{{id: 'True', value: 'Yes'}}, {{id: 'False', value: 'No'}}] }}],
                adjust:"all",
                sort: "server",
                serverFilterType: "",
                template:custom_checkbox_yesnonone,
            }}''',
            escapejs(_("Staff")))
        },
        'is_superuser': {
            'field_name': 'is_superuser',
            'datalist_column': format_lazy('''{{
                id: "is_superuser",
                header: ["{}", {{content: "serverSelectFilter" ,
                        options:[{{id: 'True', value: 'Yes'}}, {{id: 'False', value: 'No'}}] }}],
                adjust:"all",
                sort: "server",
                serverFilterType: "",
                 template:custom_checkbox_yesnonone,
            }}''',
            escapejs(_("Superuser")))
        },
        'is_active': {
            'field_name': 'is_active',
            'datalist_column': format_lazy('''{{
                id: "is_active",
                header: ["{}", {{content: "serverSelectFilter" ,
                        options:[{{id: 'True', value: 'Yes'}}, {{id: 'False', value: 'No'}}] }}],
                adjust:"all",
                sort: "server",
                serverFilterType: "",
                template:custom_checkbox_yesnonone,
            }}''',
            escapejs(_("Active")))
        },
        'groups__name': {
            'field_name': 'groups__name',
            'datalist_column': format_lazy('''{{
                id: "groups__name",
                serverFilterType:"icontains",
                adjust:"all",
                header: ["{}", {{content: "serverFilter"}}],
                sort: "server"
            }}''',
            escapejs(_("Group")))
        },
    }

    def get_list_display(self, view=None, request=None):
        _list_display = super().get_list_display(view=view, request=request)
        if apps.is_installed("hijack") and request.user.is_superuser:
            hijack_column = {
                'field_name': 'userid',
                'click_action': '''hijack_user(el['id']);''',
                'datalist_column': '''{
                    id: "userid",
                    header: ['',''],
                    adjust: "data",
                    template: 'Hijack'
                }'''
            }
            return _list_display + [hijack_column]
        else:
            return _list_display

    enable_json_loading = True
    only_superuser = True
    form_create = UserAdminCreateForm
    form_update = UserAdminUpdateForm
    change_form_template = 'django_webix/admin/account/admin_user_update.js'

    actions = [multiple_delete_action]

    def get_urls(self):
        return [
                   path(
                       '<int:pk>/password/admin',
                       self.user_change_password().as_view(),
                       name='users.user.update_password',
                   ),
               ] + super().get_urls()

    def user_change_password(self):
        _admin = self

        from django_webix.views import WebixUpdateView

        class WebixAdminUpdateView(WebixUpdateView):
            template_name = 'django_webix/admin/account/admin_password_change.js'
            url_pattern_update = 'dwadmin:users.user.update_password'
            url_pattern_list = 'dwadmin:users.user.list'
            form_class = AdminPasswordChangeForm
            model = _admin.model
            inlines = [] #_admin.inlines
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
