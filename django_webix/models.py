# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class GenericModelWebix(models.Model):
    def __init__(self, *args, **kwargs):
        from warnings import warn
        warn('`django_webix.models.GenericModelWebix` has been deprecated. '
             '`GenericModelWebix` will be removed in a future release.', DeprecationWarning)
        super(GenericModelWebix, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True
