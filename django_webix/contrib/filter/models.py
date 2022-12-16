from django.apps import apps
from django.conf import settings
from django.db import models

from django.db.models import JSONField

from django.utils.translation import gettext_lazy as _

from django_webix.contrib.filter.managers import WebixFilterManager
from django_webix.utils.filters import from_dict_to_qset

from django_dal.models import DALModel


class WebixFilter(DALModel):
    insert_date = models.DateTimeField(_('Insert date'), auto_now_add=True)
    update_date = models.DateTimeField(_('Update date'), auto_now=True)
    title = models.CharField(_('Title'), max_length=255, blank=False, null=False)
    description = models.TextField(_('Description'), blank=True, null=True)
    model = models.CharField(_('Model'), max_length=255, blank=False, null=False)
    filter = JSONField(_('Filter'), blank=True, null=True)

    insert_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Insert user'),
                                    blank=True, null=True, on_delete=models.CASCADE)
    visibility = models.CharField(_('Visiblity'), max_length=32, choices=[
        ("public", _('Public') ),
        ("private", _('Private') ),
        ("restricted", _('Restricted') ),
    ], default='public')
    assignees_groups = models.ManyToManyField('auth.Group', blank=True, verbose_name=_('Assignees groups'), )
    shared_edit_group = models.BooleanField(_('Shared edit group'), blank=True, null=False)

    objects = WebixFilterManager()

    class Meta:
        verbose_name = _('Webix Filter')
        verbose_name_plural = _('Webix Filters')

    def __str__(self):
        return "{}".format(self.title)

    def get_model_class(self):
        try:
            app_label, model = self.model.lower().split('.')
        except:
            return None
        return apps.get_model(app_label=app_label, model_name=model)

    def get_query(self):
        model_class = self.get_model_class()
        if model_class is None:
            return None
        return from_dict_to_qset(self.filter, model=model_class)

    def get_queryset_filtered(self):
        query = self.get_query()
        model_class = self.get_model_class()
        if model_class is None:
            return None
        return model_class.objects.filter(query)
