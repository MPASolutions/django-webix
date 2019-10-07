#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django import forms
from django.views.generic import TemplateView, FormView

from django_webix.forms import WebixModelForm, WebixForm
from django_webix.forms import WebixTabularInlineFormSet, WebixStackedInlineFormSet, BaseWebixInlineFormSet
from django_webix.views import WebixCreateWithInlinesView, WebixCreateWithInlinesUnmergedView, \
    WebixUpdateWithInlinesView, WebixUpdateWithInlinesUnmergedView, \
    WebixDeleteView
from .models import MyModel, InlineModel, InlineStackedModel, InlineEmptyModel, UrlsModel


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
    permissions = False


class MyModelCreateUnmergedView(WebixCreateWithInlinesUnmergedView):
    model = MyModel
    inlines = [InlineModelInline, InlineStackedModelInline, InlineEmptyModelInline]
    form_class = MyModelForm
    permissions = False

    url_create = 'app_name.mymodel.create_unmerged'


class MyModelCreateErrorView(WebixCreateWithInlinesView):
    model = MyModel
    inlines = [InlineModelInline, InlineStackedModelInline, InlineEmptyModelInline]
    form_class = MyModelForm
    style = 'error'

    url_create = 'app_name.mymodel.create_error'


class MyModelUpdateView(WebixUpdateWithInlinesView):
    model = MyModel
    inlines = [InlineModelInline, InlineStackedModelInline, InlineEmptyModelInline]
    form_class = MyModelForm


class MyModelUpdateErrorView(WebixUpdateWithInlinesView):
    model = MyModel
    inlines = [InlineModelInline, InlineStackedModelInline, InlineEmptyModelInline]
    form_class = MyModelForm
    style = 'error'

    url_create = 'app_name.mymodel.update_error'


class MyModelDeleteView(WebixDeleteView):
    model = MyModel


class InlineModelUpdateView(WebixUpdateWithInlinesUnmergedView):
    model = InlineModel
    fields = '__all__'


class InlineStackedModelDelete(WebixDeleteView):
    model = InlineStackedModel


class CreateSuccessUrlView(WebixCreateWithInlinesView):
    model = UrlsModel
    fields = '__all__'
    success_url = '/'


class CreateUrlUpdateView(WebixCreateWithInlinesView):
    model = UrlsModel
    fields = '__all__'
    url_update = 'app_name.mymodel.create_urlupdate'


class CreateUrlListView(WebixCreateWithInlinesView):
    model = UrlsModel
    fields = '__all__'
    url_update = None
    url_list = 'app_name.mymodel.create_urllist'


class CreateNoUrlView(WebixCreateWithInlinesView):
    model = UrlsModel
    fields = '__all__'
    url_update = None
    url_list = None


class UpdateSuccessUrlView(WebixUpdateWithInlinesView):
    model = UrlsModel
    fields = '__all__'
    success_url = '/'


class UpdateUrlUpdateView(WebixUpdateWithInlinesView):
    model = UrlsModel
    fields = '__all__'
    url_update = 'app_name.mymodel.update_urlupdate'


class UpdateNoUrlView(WebixUpdateWithInlinesView):
    model = UrlsModel
    fields = '__all__'
    url_update = None
    url_list = None


class DeleteSuccessUrlView(WebixDeleteView):
    model = UrlsModel
    success_url = '/'


class DeleteUrlListView(WebixDeleteView):
    model = UrlsModel
    url_list = 'app_name.mymodel.delete_urllist'


class DeleteNoUrlView(WebixDeleteView):
    model = UrlsModel
    url_update = None
    url_list = None
