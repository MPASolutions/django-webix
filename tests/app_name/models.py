#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from django_webix.models import GenericModelWebix


class MyModel(GenericModelWebix):
    field = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    floatfield = models.FloatField()
    decimalfield = models.DecimalField(decimal_places=2, max_digits=5)
    integerfield = models.IntegerField()
    integerfield_null = models.IntegerField(blank=True, null=True)
    integerfield_default = models.IntegerField(blank=True, null=True, default=43)
    readonly = models.CharField(max_length=255, blank=True, null=True)
    boolean = models.NullBooleanField(blank=True, null=True, default=True)
    datefield = models.DateField(blank=True, null=True, default=timezone.datetime.today)
    datefield_empty = models.DateField(blank=True, null=True)
    datefield_2 = models.DateField(blank=True, null=True, default="2018-01-01")
    datetimefield = models.DateTimeField(blank=True, null=True, default=timezone.now)
    datetimefield_empty = models.DateTimeField(blank=True, null=True)
    datetimefield_2 = models.DateTimeField(blank=True, null=True, default="2018-01-01T13:00:00+00:00")
    booleanfield = models.BooleanField(default=False)
    datetimefield_null = models.DateTimeField(blank=True, null=True)
    filepathfield_default = models.FilePathField(blank=True, null=True, path='/tmp', default='')

    class WebixMeta:
        url_list = 'mymodel_list'
        url_create = 'mymodel_create'
        url_update = 'mymodel_update'
        url_delete = 'mymodel_delete'

    @staticmethod
    def autocomplete_search_fields():
        return "field__icontains", "email__icontains",


class InlineModel(GenericModelWebix):
    inline_field = models.CharField(max_length=255)
    timefield = models.TimeField(blank=True, null=True, default=timezone.now)
    datefield = models.DateField(blank=True, null=True, default=timezone.datetime.today)
    datetimefield = models.DateTimeField(blank=True, null=True, default=timezone.now)
    filepathfield = models.FilePathField(blank=True, null=True, path='/tmp')
    filefield = models.FileField(blank=True, null=True)
    filefield_default = models.FileField(blank=True, null=True, default='test.txt')
    imagefield = models.ImageField(blank=True, null=True)
    imagefield_default = models.ImageField(default='image.jpg')
    booleanfield = models.BooleanField(default=False)

    my_model = models.ForeignKey(MyModel, on_delete=models.CASCADE)

    class WebixMeta:
        url_update = 'inlinemodel_update'


class InlineStackedModel(GenericModelWebix):
    textfield = models.TextField(blank=True, null=True)
    timefield = models.TimeField(blank=True, null=True)
    timefield_string = models.TimeField(blank=True, null=True, default="10:00")  # TODO: SISTEMARE
    datefield = models.DateField(blank=True, null=True)
    nullbooleanfield = models.NullBooleanField(blank=True, null=True)
    booleanfield = models.BooleanField(default=False)
    urlfield = models.URLField(blank=True, null=True, default='https://www.example.com')
    urlfield_2 = models.URLField(blank=True, null=True)
    slugfield = models.SlugField(blank=True, null=True, default='slug-field')
    slugfield_2 = models.SlugField(blank=True, null=True)
    choicefield = models.CharField(max_length=255, blank=True, null=True, choices=(
        ('test', 'Test'),
        ('sample', 'Sample')
    ), default='test')
    inlinemodel = models.ForeignKey('InlineModel', blank=True, null=True, related_name='inlinemodel_fk',
                                    on_delete=models.CASCADE)
    inlinemodels = models.ManyToManyField('InlineModel', blank=True, related_name='inlinemodel_m2m')
    inlinemodels_default = models.ManyToManyField('InlineModel', blank=True, related_name='inlinemodel_m2m_default',
                                                  default=[1])
    foreign_default = models.ForeignKey('InlineModel', blank=True, null=True, default=1, on_delete=models.CASCADE)

    my_model = models.ForeignKey(MyModel, on_delete=models.CASCADE)

    class WebixMeta:
        url_delete = 'inlinestackedmodel_delete'


class InlineEmptyModel(models.Model):
    textfield = models.TextField(blank=True, null=True)
    boolean = models.NullBooleanField(blank=True, null=True, default=2)
    choicefield = models.CharField(max_length=255, choices=(
        ('test', 'Test'),
        ('sample', 'Sample')
    ))
    foreign_default = models.ForeignKey('InlineStackedModel', on_delete=models.CASCADE)
    foreign_default_2 = models.ForeignKey('InlineStackedModel', blank=True, null=True,
                                          related_name="inlineeptymodel_fk2", on_delete=models.CASCADE)
    foreign_self = models.ForeignKey('self', on_delete=models.CASCADE)

    my_model = models.ForeignKey(MyModel, on_delete=models.CASCADE)


class SubInlineStackedModel(models.Model):
    my_model = models.ForeignKey(InlineStackedModel, on_delete=models.CASCADE)
