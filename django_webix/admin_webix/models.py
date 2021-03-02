# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from mptt.models import TreeForeignKey

from django_dal.models import DALMPTTModel as MPTTModel


class WebixAdminMenu(MPTTModel):
    label = models.CharField(verbose_name='Nome nodo', max_length=255, blank=True, null=True)
    icon = models.CharField(verbose_name='Icona', max_length=255, blank=True, null=True)
    url = models.CharField(verbose_name='Web link', max_length=1023, blank=True, null=True)
    enabled = models.BooleanField(verbose_name='Abilitato', default=True, blank=True)
    active_all = models.BooleanField(verbose_name='Attivo per tutti', default=True, blank=True)
    model = models.ForeignKey(ContentType, verbose_name='Modello', null=True, blank=True, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, blank=True, verbose_name='Gruppi per i quali è abilitato')

    # fields for mptt tree
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    # class MPTTMeta:
    #     order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Webix Admin Menu'
        verbose_name_plural = 'Webix Admin Menu'

    def __str__(self):
        if self.label:
            return self.label
        else:
            return (self.model.model_class()._meta.verbose_name_plural).title()

    @property
    def get_url(self):
        if self.model:
            return reverse('admin_webix:{app_label}.{model_name}.list'.format(app_label=self.model.app_label,
                                                                              model_name=self.model.model))
        if self.url:
            return self.url
        return ''
