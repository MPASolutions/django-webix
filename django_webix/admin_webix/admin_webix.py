# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import path

from django_webix import admin_webix as admin
from django_webix.admin_webix.forms import GroupAdminForm, AdminPasswordChangeForm
from django_webix.admin_webix.views import UserAdminCreate, UserAdminUpdate
from django_webix.views.generic.actions import multiple_delete_action


@admin.register(get_user_model())
class UserAdmin(admin.ModelWebixAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'groups__name']
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

        # if request.method == 'POST':
        #     form = self.change_password_form(user, request.POST)
        #     if form.is_valid():
        #         form.save()
        #         change_message = self.construct_change_message(request, form, None)
        #         self.log_change(request, user, change_message)
        #         msg = gettext('Password changed successfully.')
        #         messages.success(request, msg)
        #         update_session_auth_hash(request, form.user)
        #         return HttpResponseRedirect(
        #             reverse(
        #                 '%s:%s_%s_change' % (
        #                     self.admin_site.name,
        #                     user._meta.app_label,
        #                     user._meta.model_name,
        #                 ),
        #                 args=(user.pk,),
        #             )
        #         )
        # else:
        #     form = self.change_password_form(user)
        #
        # fieldsets = [(None, {'fields': list(form.base_fields)})]
        # adminForm = admin.helpers.AdminForm(form, fieldsets, {})
        #
        # context = {
        #     'title': _('Change password: %s') % escape(user.get_username()),
        #     'adminForm': adminForm,
        #     'form_url': form_url,
        #     'form': form,
        #     'is_popup': (IS_POPUP_VAR in request.POST or
        #                  IS_POPUP_VAR in request.GET),
        #     'add': True,
        #     'change': False,
        #     'has_delete_permission': False,
        #     'has_change_permission': True,
        #     'has_absolute_url': False,
        #     'opts': self.model._meta,
        #     'original': user,
        #     'save_as': False,
        #     'show_save': True,
        #     **self.admin_site.each_context(request),
        # }
        #
        # request.current_app = self.admin_site.name
        #
        # return TemplateResponse(
        #     request,
        #     self.change_user_password_template or
        #     'admin/auth/user/change_password.html',
        #     context,
        # )


@admin.register(Group)
class GroupAdmin(admin.ModelWebixAdmin):
    list_display = ['name']
    enable_json_loading = True
    only_superuser = True
    form = GroupAdminForm
