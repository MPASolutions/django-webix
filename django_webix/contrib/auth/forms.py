from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm, _unicode_ci_compare
from django.utils.translation import gettext_lazy as _

from django_webix.forms import WebixForm

UserModel = get_user_model()


class WebixPasswordResetForm(PasswordResetForm, WebixForm):
    username = forms.CharField(label=_("Username"), required=False, widget=forms.HiddenInput())

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(**{
            '%s__iexact' % email_field_name: email,
            'is_active': True,
        })
        username = self.cleaned_data.get("username")
        if username:
            active_users = active_users.filter(**{
                '%s__exact' % UserModel.USERNAME_FIELD: username
            })
        return (
            u for u in active_users
            if u.has_usable_password() and
               _unicode_ci_compare(email, getattr(u, email_field_name))
        )

    def clean(self):
        email = self.cleaned_data.get("email")
        if len(list(self.get_users(email))) > 1:
            self.add_error('username', _("Enter your username"))
            self.fields['username'].widget = forms.TextInput()
        return self.cleaned_data


class WebixSetPasswordForm(SetPasswordForm, WebixForm):
    pass
