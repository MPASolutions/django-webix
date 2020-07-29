from django_webix.forms import WebixModelForm
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordResetForm
from django_webix.forms import WebixForm, WebixModelForm


class UserForm(WebixModelForm):
    class Meta:
        localized_fields = ('__all__')
        model = get_user_model()
        fields = [i.attname for i in get_user_model()._meta.fields if i.editable and
                  all(x not in i.attname for x in
                      ['password', 'is_staff', 'is_active', 'is_superuser', 'date_joined', 'data'])]


# ######################################################## 2FA ########################################################
class FieldSetMixin:
    @staticmethod
    def authenticationForm_get_fieldsets(self):
        fs = self.get_elements

        # Customizeing fields
        fs[self.add_prefix('username')].update({"label": "Username", "labelWidth": 100})
        fs[self.add_prefix('password')].update({"type": "password", "label": "Password", "labelWidth": 100})

        return [
            {'cols': [fs[self.add_prefix('username')]]},
            {'cols': [fs[self.add_prefix('password')]]}
        ]

    @staticmethod
    def setPasswordForm_get_fieldsets(self):
        fs = self.get_elements

        # Customizeing fields
        fs[self.add_prefix('new_password1')].update({"type": "password", "labelWidth": 220})
        fs[self.add_prefix('new_password2')].update({"type": "password", "labelWidth": 220})

        return [
            {'cols': [fs[self.add_prefix('new_password1')]]},
            {'cols': [fs[self.add_prefix('new_password2')]]}
        ]


# ################################ Autenticazione a 2 fattori - django-two-factor-auth ################################
SetPasswordForm.__bases__ = (WebixForm,)
WebixSetPasswordForm = type(str('WebixSetPasswordForm'), (SetPasswordForm,),
                            {'get_fieldsets': FieldSetMixin.setPasswordForm_get_fieldsets})


# ############################################## Reset password by email ##############################################
PasswordResetForm.__bases__ = (WebixForm,)
WebixPasswordResetForm = type(str('WebixPasswordResetForm'), (PasswordResetForm,), {})
