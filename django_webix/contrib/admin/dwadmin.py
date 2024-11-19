from django.apps import apps
from django.conf import settings
from django.contrib.admin.models import LogEntry
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
from django_webix.views import WebixUpdateView
from django_webix.views.generic.actions import multiple_delete_action


class UserAdmin(admin.ModelWebixAdmin):
    def get_extra_context(self, view=None, request=None):
        context = super().get_extra_context(view, request)
        if issubclass(type(view), WebixUpdateView):
            context["auth_user_model"] = settings.AUTH_USER_MODEL.lower()
        return context

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
                minWidth:200,
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
                       name=f'{settings.AUTH_USER_MODEL.lower()}.update_password',
                   ),
               ] + super().get_urls()

    def user_change_password(self):
        _admin = self

        from django_webix.views import WebixUpdateView

        class WebixAdminUpdateView(WebixUpdateView):
            template_name = 'django_webix/admin/account/admin_password_change.js'
            url_pattern_update = f'dwadmin:{settings.AUTH_USER_MODEL.lower()}.update_password'
            url_pattern_list = f'dwadmin:{settings.AUTH_USER_MODEL.lower()}.list'
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


class LogEntryAdmin(admin.ModelWebixAdmin):

    #label_width = 300
    suggest_width = 300  # options : int | None for width as parent
    #label_align = 'left'
    ordering = ['-action_time']

    list_display = ['id', 'action_time', 'user__username', 'object_id', 'content_type__model', 'object_repr',
                    'action_flag', 'change_message', 'url']
    enable_json_loading = True
    only_superuser = True

    enable_column_copy = False
    enable_column_delete = False
    delete_permission = False
    add_permission = False
    change_permission = False

    list_display_header = {
        'user__username': {
            'field_name': 'user__username',
            'datalist_column': format_lazy('''{{
                id: "user__username",
                header: [{{text:"{}"}},
                        {{content: "serverRichSelectFilter",
                            options:user__username_options,
                            inputConfig:{{ suggest: {{fitMaster: false}} }} }}],
                adjust:"all",
                sort: "server",
                serverFilterType: "iexact",
                collection: user__username_options
            }}''',
            escapejs(_("User")))
        },
        'id': {
            'field_name': 'id',
            'datalist_column': format_lazy('''{{
                id: "id",
                header: ["{}", {{content: "serverFilter" }}],
                adjust: "all",
                sort: "server",
                serverFilterType: "numbercompare",
                css:{{'text-align':'right'}}
            }}''',
            escapejs(_("ID")))
        },
        'object_id': {
            'field_name': 'object_id',
            'datalist_column': format_lazy('''{{
                    id: "object_id",
                    header: [{{text:"{}"}}, {{content: "serverFilter" }}],
                    adjust:"all",
                    sort: "server",
                    serverFilterType: "icontains",
                    css:{{'text-align':'right'}}
                }}''',
                escapejs(_("Object ID")))
        },
        'content_type__model': {
            'field_name': 'content_type__model',
            'datalist_column': format_lazy('''{{
                    id: "content_type__model",
                    header: [{{text:"{}"}}, {{content: "serverFilter" }}],
                    adjust:"all",
                    sort: "server",
                    serverFilterType: "icontains",
                }}''',
                escapejs(_("Data type")))
        },
        'object_repr': {
            'click_action': '''load_js(el['url'])''',
            'field_name': 'object_repr',
            'datalist_column': format_lazy('''{{
                    id: "object_repr",
                    header: [{{text:"{}"}}, {{content: "serverFilter" }}],
                    adjust:"all",
                    sort: "server",
                    serverFilterType: "icontains",
                    css:{{'color':'blue'}}
                }}''',
                escapejs(_("Object")))
        },
        'action_flag': {
            'field_name': 'action_flag',
            'datalist_column': format_lazy('''{{
                    id: "action_flag",
                    header: [{{text:"{}"}},
                            {{content: "serverRichSelectFilter",
                                options: action_flag_options,
                                inputConfig:{{ suggest: {{fitMaster: false}} }} }}],
                    adjust:"all",
                    sort: "server",
                    serverFilterType: "iexact",
                    collection: action_flag_options
                }}''',
                escapejs(_("Action")))
        },
        'change_message': {
            'field_name': 'change_message',
            'datalist_column': format_lazy('''{{
                    id: "change_message",
                    header: [{{text:"{}"}}, {{content: "serverFilter" }}],
                    fillspace:true,
                    sort: "server",
                    serverFilterType: "icontains",
                }}''',
                escapejs(_("Informations")))
        },
        'url': {
            'field_name': 'url',
            'queryset_exclude': True,
            'datalist_column': '{id: "url", hidden: true}'
        },
    }

    def _get_objects_datatable_values(self, view, qs):
        data = super(view.__class__, view)._get_objects_datatable_values(qs)
        for item, value in zip(qs, data):
            value.update({
                'url': self.admin_site.get_object_url(item.content_type,
                                                object_pk=item.object_id)
            })
        return data


admin.site.register(LogEntry, admin_class=LogEntryAdmin)
