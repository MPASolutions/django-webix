from django_webix.views import WebixUpdateView, WebixCreateView
from django_webix.admin_webix.forms import UserForm, UserAdminUpdateForm, UserAdminCreateForm
from django.contrib.auth import get_user_model


class UserUpdate(WebixUpdateView):
    model = get_user_model()
    form_class = UserForm
    enable_button_save_continue = False
    enable_button_save_addanother = False
    success_url = '.'
    url_pattern_update = 'admin_webix:account_update'


class UserAdminCreate(WebixCreateView):
    model = get_user_model()
    form_class = UserAdminCreateForm

    def get_url_pattern_update(self):
        return 'admin_webix:' + super().get_url_pattern_update()

    def get_url_pattern_list(self):
        return 'admin_webix:' + super().get_url_pattern_list()

    def get_url_pattern_delete(self):
        return 'admin_webix:' + super().get_url_pattern_delete()

    def get_url_pattern_create(self):
        return 'admin_webix:' + super().get_url_pattern_create()


class UserAdminUpdate(WebixUpdateView):
    model = get_user_model()
    form_class = UserAdminUpdateForm
    template_name = 'admin_webix/account/admin_user_update.js'

    def get_url_pattern_update(self):
        return 'admin_webix:' + super().get_url_pattern_update()

    def get_url_pattern_list(self):
        return 'admin_webix:' + super().get_url_pattern_list()

    def get_url_pattern_delete(self):
        return 'admin_webix:' + super().get_url_pattern_delete()

    def get_url_pattern_create(self):
        return 'admin_webix:' + super().get_url_pattern_create()
