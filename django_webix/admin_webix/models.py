# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from mptt.models import TreeForeignKey
from django.utils.translation import ugettext as _

from django_dal.mptt_managers import DALTreeManager
from django_dal.models import DALMPTTModel as MPTTModel


class WebixAdminMenu(MPTTModel):
    objects = DALTreeManager()

    label = models.CharField(verbose_name=_('Node name'), max_length=255, blank=True, null=True)
    icon = models.CharField(verbose_name=_('Icon'), max_length=255, blank=True, null=True)
    url = models.CharField(verbose_name=_('Web link'), max_length=1023, blank=True, null=True)
    enabled = models.BooleanField(verbose_name=_('Enabled'), default=True, blank=True)
    active_all = models.BooleanField(verbose_name=_('Active for all'), default=True, blank=True)
    model = models.ForeignKey(ContentType, verbose_name=_('Model'), null=True, blank=True, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, blank=True, verbose_name=_('Enabled groups'))
    prefix = models.CharField(verbose_name=_('Prefix'), max_length=1023, blank=True, null=True)
    # fields for mptt tree
    parent = TreeForeignKey('self', on_delete=models.CASCADE, verbose_name=_('Parent'), null=True, blank=True, related_name='children')

    # class MPTTMeta:
    #     order_insertion_by = ['name']

    class Meta:
        verbose_name = _('Webix Admin Menu')
        verbose_name_plural = _('Webix Admin Menu')

    def __str__(self):
        if self.label:
            return self.label
        else:
            return (self.model.model_class()._meta.verbose_name_plural).title()

    @property
    def get_url(self):
        if self.model:
            if self.prefix not in ['', None]:
                return reverse('admin_webix:{app_label}.{model_name}.list.{prefix}'.format(app_label=self.model.app_label,
                                                                                           model_name=self.model.model,
                                                                                           prefix=self.prefix) )
            else:
                return reverse('admin_webix:{app_label}.{model_name}.list'.format(app_label=self.model.app_label,
                                                                              model_name=self.model.model))
        if self.url:
            return self.url
        return ''
