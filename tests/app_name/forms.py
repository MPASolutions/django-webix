#!/usr/bin/env python

from django import forms

from django_webix.forms import (WebixModelForm, WebixForm, WebixTabularInlineFormSet, WebixStackedInlineFormSet)
from django_webix.forms.formsets import BaseWebixInlineFormSet
from .models import (MyModel, InlineModel, InlineStackedModel, InlineEmptyModel)


class MyLoginForm(WebixForm):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)


class InlineModelInline(WebixTabularInlineFormSet):
    model = InlineModel
    fields = '__all__'

    def get_queryset(self):
        return self.inline_model.objects.all()


class InlineStackedModelForm(WebixModelForm):
    min_count_suggest = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autocomplete_fields = ['inlinemodel']

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
