from django_webix.views import WebixUpdateView
from django.conf import settings
from django_webix.admin_webix.forms import UserForm
# from django.db.models.loading import get_model
from django.contrib.auth import get_user_model


class UserUpdate(WebixUpdateView):
    model = get_user_model()
    form_class = UserForm
    enable_button_save_continue = False
    enable_button_save_addanother = False
    success_url = '.'
    url_pattern_update = 'admin_webix:account_update'
