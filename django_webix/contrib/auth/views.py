from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy, reverse
from django_webix.contrib.auth.forms import WebixPasswordResetForm, WebixSetPasswordForm
from django_webix.views import WebixTemplateView, WebixFormView


class WebixPasswordResetContainerView(WebixTemplateView):
    template_name = "django_webix/auth/password_reset/base.js"


class WebixPasswordResetView(auth_views.PasswordResetView, WebixFormView):
    template_name = 'django_webix/auth/password_reset/password_reset_form.js'
    email_template_name = 'django_webix/auth/password_reset/password_reset_email.html'
    subject_template_name = 'django_webix/auth/password_reset/password_reset_subject.txt'
    form_class = WebixPasswordResetForm
    success_url = reverse_lazy('dwauth.password_reset.done')
    url_pattern_send = "dwauth.password_reset.form"


class WebixPasswordResetDoneView(auth_views.PasswordResetDoneView, WebixTemplateView):
    template_name = 'django_webix/auth/password_reset/password_reset_done.js'


class WebixPasswordResetConfirmView(auth_views.PasswordResetConfirmView, WebixFormView):
    form_class = WebixSetPasswordForm
    success_url = reverse_lazy('dwauth.password_reset.complete')
    template_name = 'django_webix/auth/password_reset/password_reset_confirm.js'

    def get_url_send(self):
        return reverse("dwauth.password_reset.confirm", kwargs={
            "uidb64": self.kwargs.get('uidb64'),
            'token': self.kwargs.get('token'),
        })


class WebixPasswordResetCompleteView(auth_views.PasswordResetCompleteView, WebixTemplateView):
    template_name = 'django_webix/auth/password_reset/password_reset_complete.js'
