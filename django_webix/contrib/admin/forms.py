from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from django_webix.forms import WebixForm, WebixModelForm


class GroupAdminForm(WebixModelForm):
    class Meta:
        localized_fields = "__all__"
        model = Group
        fields = ["name", "permissions"]

    @property
    def get_elements(self):
        fs = super().get_elements
        fs["permissions"].update(
            {
                "view": "dbllist",
                "list": {"scroll": True},
                "labelLeft": _("Available permissions"),
                "labelRight": _("Selected"),
                "data": [
                    {"id": "{}".format(getattr(record, "pk")), "value": "{}".format(record)}
                    for record in Permission.objects.all()
                ],
            }
        )
        return fs


class UserForm(WebixModelForm):
    class Meta:
        localized_fields = "__all__"
        model = get_user_model()
        fields = [
            i.name
            for i in get_user_model()._meta.fields
            if i.editable
            and i.attname
            not in ["password", "is_staff", "is_active", "is_superuser", "date_joined", "data", "last_login"]
        ]

    @property
    def get_elements(self):
        fs = super().get_elements
        fs["username"].update({"readonly": "readonly", "disabled": True})
        return fs


class UserAdminCreateForm(WebixModelForm):
    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        localized_fields = "__all__"
        model = get_user_model()
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs["autofocus"] = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error("password2", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    @property
    def get_elements(self):
        fs = super().get_elements
        fs["password1"].update({"type": "password"})
        fs["password2"].update({"type": "password"})
        return fs


class UserAdminUpdateForm(WebixModelForm):
    class Meta:
        localized_fields = "__all__"
        model = get_user_model()
        fields = [
            "username",
            "is_superuser",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
        ]

    @property
    def get_elements(self):
        fs = super().get_elements
        fs["username"].update({"readonly": "readonly", "disabled": True})

        fs["groups"].update(
            {
                "view": "dbllist",
                "list": {"scroll": True},
                "labelLeft": _("Available permissions"),
                "labelRight": _("Selected"),
                "data": fs["groups"]["suggest"]["body"]["data"],
            }
        )
        fs["user_permissions"].update(
            {
                "view": "dbllist",
                "list": {"scroll": True},
                "labelLeft": _("Available permissions"),
                "labelRight": _("Selected"),
                "data": [
                    {"id": "{}".format(getattr(record, "pk")), "value": "{}".format(record)}
                    for record in Permission.objects.all()
                ],
            }
        )
        return fs

    def get_fieldsets(self, **kwargs):
        fs = self.get_elements

        return [
            {
                "id": "tabs_generali",
                "view": "tabbar",
                "value": "dettagli",
                "optionWidth": 200,
                "multiview": True,
                "options": [
                    {"id": "dettagli", "value": _("Private data")},
                    {"id": "informazioni_personali", "value": _("Personal informations")},
                    {"id": "permessi", "value": _("Permissions")},
                    {"id": "gruppi", "value": _("Groups")},
                ],
            },
            {
                "animate": False,
                "id": "tabs-principali",
                "borderless": True,
                "cells": [
                    {
                        "view": "scrollview",
                        "id": "dettagli",
                        "minHeight": 500,
                        "scroll": "y",
                        "body": {
                            "rows": [
                                {"cols": [fs["username"]]},
                                {
                                    "cols": [
                                        {
                                            "width": 300,
                                            "view": "button",
                                            "label": _("Change password"),
                                            "click": "reset();",
                                        },
                                        {},
                                    ]
                                },
                            ]
                        },
                    },
                    {
                        "view": "scrollview",
                        "id": "informazioni_personali",
                        "minHeight": 500,
                        "scroll": "y",
                        "body": {
                            "rows": [
                                {"cols": [fs["first_name"]]},
                                {"cols": [fs["last_name"]]},
                                {"cols": [fs["email"]]},
                            ]
                        },
                    },
                    {
                        "view": "scrollview",
                        "id": "permessi",
                        "minHeight": 500,
                        "scroll": "y",
                        "body": {
                            "rows": [
                                {"cols": [fs["is_active"]]},
                                {"cols": [fs["is_staff"]]},
                                {"cols": [fs["is_superuser"]]},
                                {"cols": [fs["user_permissions"]]},
                            ]
                        },
                    },
                    {
                        "view": "scrollview",
                        "id": "gruppi",
                        "minHeight": 500,
                        "scroll": "y",
                        "body": {
                            "rows": [
                                {"cols": [fs["groups"]]},
                            ]
                        },
                    },
                ],
            },
        ]


class AdminPasswordChangeForm(WebixModelForm):
    """
    A form used to change the password of a user in the admin interface.
    """

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    required_css_class = "required"
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "autofocus": True}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        localized_fields = "__all__"
        model = get_user_model()
        fields = ["username"]

    @property
    def get_elements(self):
        fs = super().get_elements
        fs["username"].update({"readonly": "readonly", "disabled": True})
        fs["password1"].update({"type": "password"})
        fs["password2"].update({"type": "password"})
        return fs

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages["password_mismatch"],
                    code="password_mismatch",
                )
        password_validation.validate_password(password2, self.instance)
        return password2

    def save(self, commit=True):
        """Save the new password."""
        password = self.cleaned_data["password1"]
        self.instance.set_password(password)
        if commit:
            self.instance.save()
        return self.instance

    @property
    def changed_data(self):
        data = super().changed_data
        for name in self.fields:
            if name not in data:
                return []
        return ["password"]


if "django_webix.contrib.admin" in settings.INSTALLED_APPS:
    from django_webix.contrib.admin.models import WebixAdminMenu

    class WebixAdminMenuForm(forms.ModelForm):
        class Meta:
            model = WebixAdminMenu
            fields = ["parent", "label", "url", "model", "enabled", "active_all", "groups"]


# ######################################################## 2FA ########################################################
class FieldSetMixin:
    @staticmethod
    def authenticationForm_get_fieldsets(self):
        fs = self.get_elements

        # Customizeing fields
        fs[self.add_prefix("username")].update({"label": "Username", "labelWidth": 100})
        fs[self.add_prefix("password")].update({"type": "password", "label": "Password", "labelWidth": 100})

        return [{"cols": [fs[self.add_prefix("username")]]}, {"cols": [fs[self.add_prefix("password")]]}]

    @staticmethod
    def setPasswordForm_get_fieldsets(self):
        fs = self.get_elements

        # Customizeing fields
        fs[self.add_prefix("new_password1")].update({"type": "password", "labelWidth": 220})
        fs[self.add_prefix("new_password2")].update({"type": "password", "labelWidth": 220})

        return [{"cols": [fs[self.add_prefix("new_password1")]]}, {"cols": [fs[self.add_prefix("new_password2")]]}]


def change_form_class(bases):
    if WebixForm not in bases and forms.Form in bases:
        bases = tuple([x if x != forms.Form else WebixForm for x in bases])
    return bases


def change_model_form_class(bases):
    if WebixModelForm not in bases and forms.ModelForm in bases:
        bases = tuple([x if x != forms.ModelForm else WebixModelForm for x in bases])
    return bases


if apps.is_installed("two_factor"):

    # from django_otp.forms import OTPAuthenticationFormMixin
    from two_factor.forms import (
        AuthenticationTokenForm,
        BackupTokenForm,
        DeviceValidationForm,
        DisableForm,
        MethodForm,
        TOTPDeviceForm,
    )

    # ################################ Autenticazione a 2 fattori - django-two-factor-auth ############################
    AuthenticationForm.__bases__ = change_form_class(AuthenticationForm.__bases__)
    WebixAuthenticationAuthForm = type(
        str("WebixAuthenticationAuthForm"),
        (AuthenticationForm,),
        {"get_fieldsets": FieldSetMixin.authenticationForm_get_fieldsets},
    )

    AuthenticationTokenForm.__bases__ = change_form_class(AuthenticationTokenForm.__bases__)
    WebixAuthenticationTokenForm = type(str("WebixAuthenticationTokenForm"), (AuthenticationTokenForm,), {})

    BackupTokenForm.__bases__ = (WebixAuthenticationTokenForm,)
    WebixAuthenticationBackupTokenForm = type(str("WebixAuthenticationBackupTokenForm"), (BackupTokenForm,), {})

    SetPasswordForm.__bases__ = change_form_class(SetPasswordForm.__bases__)
    WebixSetPasswordForm = type(
        str("WebixSetPasswordForm"), (SetPasswordForm,), {"get_fieldsets": FieldSetMixin.setPasswordForm_get_fieldsets}
    )

    DisableForm.__bases__ = change_form_class(DisableForm.__bases__)
    WebixDisableForm = type(str("WebixDisableForm"), (DisableForm,), {})

    MethodForm.__bases__ = change_form_class(MethodForm.__bases__)
    WebixMethodForm = type(str("WebixMethodForm"), (MethodForm,), {})

    TOTPDeviceForm.__bases__ = change_form_class(TOTPDeviceForm.__bases__)
    WebixTOTPDeviceForm = type(str("WebixTOTPDeviceForm"), (TOTPDeviceForm,), {})

    if apps.is_installed("two_factor.plugins.phonenumber"):

        # noinspection PyUnresolvedReferences
        from two_factor.plugins.phonenumber.forms import PhoneNumberForm

        PhoneNumberForm.__bases__ = change_model_form_class(PhoneNumberForm.__bases__)
        WebixPhoneNumberForm = type(str("WebixPhoneNumberForm"), (PhoneNumberForm,), {})

    DeviceValidationForm.__bases__ = change_form_class(DeviceValidationForm.__bases__)
    WebixDeviceValidationForm = type(str("WebixDeviceValidationForm"), (DeviceValidationForm,), {})

    if apps.is_installed("two_factor.plugins.yubikey"):
        # noinspection PyUnresolvedReferences
        from two_factor.plugins.yubikey.forms import YubiKeyDeviceForm

        YubiKeyDeviceForm.__bases__ = (WebixDeviceValidationForm,)
        WebixYubiKeyDeviceForm = type(str("WebixYubiKeyDeviceForm"), (YubiKeyDeviceForm,), {})

    # ############################################## Reset password by email ##########################################
    PasswordResetForm.__bases__ = change_form_class(PasswordResetForm.__bases__)
    WebixPasswordResetForm = type(str("WebixPasswordResetForm"), (PasswordResetForm,), {"label_width": 60})
else:
    AuthenticationForm.__bases__ = change_form_class(AuthenticationForm.__bases__)
    WebixAuthenticationAuthForm = type(
        str("WebixAuthenticationAuthForm"),
        (AuthenticationForm,),
        {"get_fieldsets": FieldSetMixin.authenticationForm_get_fieldsets},
    )

    #    AuthenticationTokenForm.__bases__ = (OTPAuthenticationFormMixin, WebixForm)
    #    WebixAuthenticationTokenForm = type(str('WebixAuthenticationTokenForm'), (AuthenticationTokenForm,), {})

    #    BackupTokenForm.__bases__ = (WebixAuthenticationTokenForm,)
    #    WebixAuthenticationBackupTokenForm = type(str('WebixAuthenticationBackupTokenForm'), (BackupTokenForm,), {})

    SetPasswordForm.__bases__ = change_form_class(SetPasswordForm.__bases__)
    WebixSetPasswordForm = type(
        str("WebixSetPasswordForm"), (SetPasswordForm,), {"get_fieldsets": FieldSetMixin.setPasswordForm_get_fieldsets}
    )

    #    DisableForm.__bases__ = (WebixForm,)
    #    WebixDisableForm = type(str('WebixDisableForm'), (DisableForm,), {})

    #    MethodForm.__bases__ = (WebixForm,)
    #    WebixMethodForm = type(str('WebixMethodForm'), (MethodForm,), {})

    #    TOTPDeviceForm.__bases__ = (WebixForm,)
    #    WebixTOTPDeviceForm = type(str('WebixTOTPDeviceForm'), (TOTPDeviceForm,), {})

    #    PhoneNumberForm.__bases__ = (WebixModelForm,)
    #    WebixPhoneNumberForm = type(str('WebixPhoneNumberForm'), (PhoneNumberForm,), {})

    #    DeviceValidationForm.__bases__ = (WebixForm,)
    #    WebixDeviceValidationForm = type(str('WebixDeviceValidationForm'), (DeviceValidationForm,), {})

    #    YubiKeyDeviceForm.__bases__ = (WebixDeviceValidationForm,)
    #    WebixYubiKeyDeviceForm = type(str('WebixYubiKeyDeviceForm'), (YubiKeyDeviceForm,), {})

    # ############################################## Reset password by email ##########################################
    PasswordResetForm.__bases__ = change_form_class(PasswordResetForm.__bases__)
    WebixPasswordResetForm = type(str("WebixPasswordResetForm"), (PasswordResetForm,), {"label_width": 60})
