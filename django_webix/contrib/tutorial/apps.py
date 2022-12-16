from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class TutorialConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "django_webix.contrib.tutorial"
    label = 'dwtutorial'
    verbose_name = _("Django Webix Tutorial")
