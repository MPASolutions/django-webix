# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.forms.fields import IntegerField
from django.forms.formsets import TOTAL_FORM_COUNT, INITIAL_FORM_COUNT, MIN_NUM_FORM_COUNT, MAX_NUM_FORM_COUNT
from django.forms.widgets import HiddenInput
from django.utils.functional import cached_property
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from extra_views import InlineFormSetFactory

from django_webix.forms import WebixForm, WebixModelForm


class WebixManagementForm(WebixForm):
    """
    ``ManagementForm`` is used to keep track of how many form instances
    are displayed on the page. If adding new forms via javascript, you should
    increment the count field of this form as well.
    """

    def __init__(self, *args, **kwargs):
        self.base_fields[TOTAL_FORM_COUNT] = IntegerField(widget=HiddenInput)
        self.base_fields[INITIAL_FORM_COUNT] = IntegerField(widget=HiddenInput)
        # MIN_NUM_FORM_COUNT and MAX_NUM_FORM_COUNT are output with the rest of
        # the management form, but only for the convenience of client-side
        # code. The POST value of them returned from the client is not checked.
        self.base_fields[MIN_NUM_FORM_COUNT] = IntegerField(required=False, widget=HiddenInput)
        self.base_fields[MAX_NUM_FORM_COUNT] = IntegerField(required=False, widget=HiddenInput)
        super(WebixManagementForm, self).__init__(*args, **kwargs)


class BaseWebixInlineFormSet(BaseInlineFormSet):
    def __init__(self, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BaseWebixInlineFormSet, self).__init__(**kwargs)

    def get_form_kwargs(self, index):
        _form_kwargs = super(BaseWebixInlineFormSet, self).get_form_kwargs(index)
        _form_kwargs.update({'request': self.request, 'inline_id': index})
        return _form_kwargs

    def get_rules(self):
        """ Returns a dict with the inline fields rules """

        result = {}
        for form in self.initial_forms:
            result.update(form.get_rules())
        return result

    def get_rules_template(self):
        """Returns the rules template"""

        rules_old = self.form(**{'request':self.request}).get_rules() or {}
        rules_old.pop(self.fk.name, None)  # Remove fk rule
        rules_new = {}
        for key in rules_old:
            rules_new['{}-__prefix__-{}'.format(self.prefix, key)] = rules_old[key]
        return rules_new

    def get_name(self):
        if self.model is not None:
            return capfirst(self.model._meta.verbose_name_plural)
        return ""  # pragma: no cover

    @cached_property
    def management_form(self):
        """Returns the ManagementForm instance for this FormSet."""

        if self.is_bound:
            form = WebixManagementForm(self.data, auto_id=self.auto_id, prefix=self.prefix)
            if not form.is_valid():
                raise ValidationError(
                    _('ManagementForm data is missing or has been tampered with'),
                    code='missing_management_form',
                )
        else:
            form = WebixManagementForm(auto_id=self.auto_id, prefix=self.prefix, initial={
                TOTAL_FORM_COUNT: self.total_form_count(),
                INITIAL_FORM_COUNT: self.initial_form_count(),
                MIN_NUM_FORM_COUNT: self.min_num,
                MAX_NUM_FORM_COUNT: self.max_num
            })
        return form


class WebixInlineFormSet(InlineFormSetFactory):
    template_name = None

    def __init__(self, parent_model, request, instance, view_kwargs=None, view=None):
        super(WebixInlineFormSet, self).__init__(parent_model, request, instance, view_kwargs, view)

        # Set form class
        if self.form_class is None:
            self.form_class = WebixModelForm

        # Set formset class
        if hasattr(self, 'custom_formset_class'):
            self.formset_class = self.custom_formset_class
        else:
            self.formset_class = BaseWebixInlineFormSet
        self.formset_class = type(str('WebixInlineFormSet'), (self.formset_class,), {'template_name': self.template_name})

        # Set queryset
        if hasattr(self, 'get_queryset') and callable(self.get_queryset):
            self.formset_kwargs['queryset'] = self.get_queryset()
        else:
            self.formset_kwargs['queryset'] = self.inline_model.objects.all()

    def get_formset_kwargs(self):
        _formset_kwargs = super(WebixInlineFormSet, self).get_formset_kwargs()
        _formset_kwargs.update({'request': self.request})
        return _formset_kwargs


class WebixStackedInlineFormSet(WebixInlineFormSet):
    template_name = 'django_webix/include/edit_inline/stacked.js'
    style = 'stacked'
    def __init__(self, parent_model, request, instance, view_kwargs=None, view=None):
        super(WebixStackedInlineFormSet, self).__init__(parent_model, request, instance, view_kwargs, view)
        self.form_class = type(str('WebixStackedModelForm'), (self.form_class,), {'style': self.style})


class WebixTabularInlineFormSet(WebixInlineFormSet):
    template_name = 'django_webix/include/edit_inline/tabular.js'
    style = 'tabular'
    def __init__(self, parent_model, request, instance, view_kwargs=None, view=None):
        super(WebixTabularInlineFormSet, self).__init__(parent_model, request, instance, view_kwargs, view)
        self.form_class = type(str('WebixTabularModelForm'), (self.form_class,), {'style': self.style})
