from django.utils.translation import gettext_lazy as _

from django_webix.contrib.extra_fields.forms import ModelFieldValueForm
from django_webix.contrib.extra_fields.models import ModelFieldValue
from django_webix.forms.formsets_generic import WebixGenericTabularInlineFormSet, BaseGenericWebixInlineFormSet


class ModelFieldValueFormSet(BaseGenericWebixInlineFormSet):
    def clean(self):
        super().clean()
        model_fields = []
        for form in self.forms:
            if 'model_field' in form.cleaned_data:
                if form.cleaned_data['model_field'] not in model_fields:
                    model_fields.append(form.cleaned_data['model_field'])
                else:
                    form.add_error('model_field', _('This choice has already been filled in.'))


class ModelFieldValueInline(WebixGenericTabularInlineFormSet):
    template_name = 'django_webix/extra_fields/edit_inline/tabular.js'
    prefix = 'modelfieldvalue_set'
    model = ModelFieldValue
    form_class = ModelFieldValueForm
    custom_formset_class = ModelFieldValueFormSet
    factory_kwargs = {'extra': 0}
