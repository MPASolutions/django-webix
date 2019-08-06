# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class GenericModelWebix(models.Model):
    class Meta:
        abstract = True

    class WebixMeta:
        url_list = None
        url_create = None
        url_update = None
        url_delete = None

    @property
    def get_model_name(self):
        return '%s.%s' % (self._meta.app_label, self._meta.model_name)

    @property
    def get_url_list(self):
        if hasattr(self.WebixMeta, 'url_list') and self.WebixMeta.url_list is not None:
            return self.WebixMeta.url_list
        return None

    @property
    def get_url_create(self):
        if hasattr(self.WebixMeta, 'url_create') and self.WebixMeta.url_create is not None:
            return self.WebixMeta.url_create
        return None

    @property
    def get_url_update(self):
        if hasattr(self.WebixMeta, 'url_update') and self.WebixMeta.url_update is not None:
            return self.WebixMeta.url_update
        return None

    @property
    def get_url_delete(self):
        if hasattr(self.WebixMeta, 'url_delete') and self.WebixMeta.url_delete is not None:
            return self.WebixMeta.url_delete
        return None
