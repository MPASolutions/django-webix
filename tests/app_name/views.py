#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django import forms
from django.views.generic import TemplateView, FormView

from django_webix.forms import WebixModelForm, WebixForm
from django_webix.formsets import WebixTabularInlineFormSet, WebixStackedInlineFormSet, BaseWebixInlineFormSet
from django_webix.views import WebixCreateWithInlinesView, WebixUpdateWithInlinesView, WebixDeleteView

from .models import MyModel, InlineModel, InlineStackedModel, InlineEmptyModel


class MyLoginForm(WebixForm):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)


class MyLoginView(FormView):
    form_class = MyLoginForm
    template_name = 'django_webix/generic/create.js'


class InlineModelInline(WebixTabularInlineFormSet):
    model = InlineModel
    fields = '__all__'

    def get_queryset(self):
        return self.inline_model.objects.all()


class InlineStackedModelForm(WebixModelForm):
    autocomplete_fields = ['inlinemodel']
    min_count_suggest = 0

    class Meta:
        model = InlineStackedModel
        fields = '__all__'


class InlineStackedModelInline(WebixStackedInlineFormSet):
    model = InlineStackedModel
    fields = '__all__'
    form_class = InlineStackedModelForm


class InlineEmptyModelForm(WebixModelForm):
    factory_kwargs = {
        'extra': 0
    }


class InlineEmptyModelFormSet(BaseWebixInlineFormSet):
    def get_queryset(self):
        return self.queryset


class InlineEmptyModelInline(WebixTabularInlineFormSet):
    model = InlineEmptyModel
    fields = '__all__'
    form_class = InlineEmptyModelForm
    custom_formset_class = InlineEmptyModelFormSet


class MyModelForm(WebixModelForm):
    readonly_fields = ['readonly', 'raise_error', 'datetimefield', 'datefield', 'booleanfield', 'datefield_empty',
                       'datetimefield_empty']

    class Meta:
        model = MyModel
        fields = '__all__'


class MyModelListView(TemplateView):
    template_name = 'list.js'

    def get_context_data(self, **kwargs):
        context = super(MyModelListView, self).get_context_data(**kwargs)
        context['datalist'] = json.dumps([{
            'id': i.pk,
            'field': i.field
        } for i in MyModel.objects.all()])
        return context


class MyModelCreateView(WebixCreateWithInlinesView):
    model = MyModel
    inlines = [InlineModelInline, InlineStackedModelInline, InlineEmptyModelInline]
    form_class = MyModelForm


class MyModelUpdateView(WebixUpdateWithInlinesView):
    model = MyModel
    inlines = [InlineModelInline, InlineStackedModelInline, InlineEmptyModelInline]
    form_class = MyModelForm


class MyModelDeleteView(WebixDeleteView):
    model = MyModel


class InlineModelUpdateView(WebixUpdateWithInlinesView):
    model = InlineModel


class InlineStackedModelDelete(WebixDeleteView):
    model = InlineStackedModel
