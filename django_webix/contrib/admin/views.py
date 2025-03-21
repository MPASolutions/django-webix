from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView
from django.http import Http404
from django.utils.translation import gettext as _
from django_webix.contrib.admin.forms import UserForm
from django_webix.views import WebixUpdateView


class UserUpdate(WebixUpdateView):
    model = get_user_model()
    form_class = UserForm
    enable_button_save_continue = False
    enable_button_save_addanother = False
    success_url = "."
    url_pattern_update = "dwadmin:account_update"

    def get_object(self, queryset=None):
        if getattr(self, "object", None) is not None:
            return self.object

        if queryset is None:
            queryset = self.get_queryset()

        queryset = queryset.filter(pk=self.request.user.pk)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query") % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj


class PasswordResetConfirmViewCustom(PasswordResetConfirmView):

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as e:
            form.add_error("new_password1", e)
            return self.render_to_response(self.get_context_data(form=form))


class PasswordChangeViewCustom(PasswordChangeView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if apps.is_installed("gdpr"):
            from gdpr.forms import GDPRPasswordChangeForm as AdminPasswordChangeForm
        else:
            from django.contrib.admin.forms import AdminPasswordChangeForm
        self.form_class = AdminPasswordChangeForm

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as e:
            form.add_error("new_password1", e)
            return self.render_to_response(self.get_context_data(form=form))
