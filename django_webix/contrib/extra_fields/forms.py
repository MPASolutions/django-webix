from django import forms
from django.contrib.contenttypes.models import ContentType
from django_webix.contrib.extra_fields.models import (
    ModelField,
    ModelFieldChoice,
    ModelFieldValue,
    get_ct_models_with_extra_fields,
)
from django_webix.forms import WebixModelForm


class ModelFieldCreateForm(WebixModelForm):
    class Meta:
        localized_fields = "__all__"
        model = ModelField
        fields = ["content_type", "label", "field_name", "field_type", "related_to", "locked"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autocomplete_fields_exclude = ["content_type", "related_to"]
        self.fields["content_type"].queryset = self.fields["content_type"].queryset.filter(
            id__in=[i.pk for i in get_ct_models_with_extra_fields()]
        )

    def get_fieldsets(self, **kwargs):
        fs = self.get_elements
        return [
            {"cols": [fs["content_type"], fs["label"]]},
            {"cols": [fs["field_name"], fs["field_type"]]},
            {"cols": [fs["related_to"]]},
            {"cols": [fs["locked"]]},
        ]


class ModelFieldUpdateForm(ModelFieldCreateForm):
    def get_fieldsets(self, **kwargs):
        fs = self.get_elements

        fs["content_type"].update({"disabled": True})
        fs["field_name"].update({"disabled": True})
        fs["field_type"].update({"disabled": True})
        fs["related_to"].update({"disabled": True})

        return [
            {"cols": [fs["content_type"], fs["label"]]},
            {"cols": [fs["field_name"], fs["field_type"]]},
            {"cols": [fs["related_to"]]},
            {"cols": [fs["locked"]]},
        ]


class ModelFieldChoiceForm(WebixModelForm):
    class Meta:
        localized_fields = "__all__"
        model = ModelFieldChoice
        fields = ["key", "value"]


class ModelFieldValueForm(WebixModelForm):
    class Meta:
        localized_fields = "__all__"
        model = ModelFieldValue
        fields = ["model_field", "value"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.parent_model is not None:
            content_type = ContentType.objects.get_for_model(self.parent_model)
            self.fields["model_field"].queryset = self.fields["model_field"].queryset.filter(content_type=content_type)

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get("model_field", None) is not None and cleaned_data.get("value", None) is not None:
            mf = cleaned_data.get("model_field", None)
            model_field_class = getattr(forms, mf.field_type)

            class _Form(forms.Form):
                field = model_field_class()

            _form = _Form({"field": cleaned_data.get("value", None)})
            if not _form.is_valid():
                self.add_error("model_field", _form.errors["field"])

        return cleaned_data
