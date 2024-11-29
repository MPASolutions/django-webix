from django_webix.contrib import admin
from django_webix.contrib.extra_fields.forms import ModelFieldChoiceForm, ModelFieldCreateForm, ModelFieldUpdateForm
from django_webix.contrib.extra_fields.models import ModelFieldChoice
from django_webix.forms import WebixTabularInlineFormSet


class ModelFieldChoiceInline(WebixTabularInlineFormSet):
    model = ModelFieldChoice
    form_class = ModelFieldChoiceForm


class ModelFieldAdmin(admin.ModelWebixAdmin):
    form_create = ModelFieldCreateForm
    form_update = ModelFieldUpdateForm
    inlines = [ModelFieldChoiceInline]
    list_display = ["content_type__model", "label", "field_name", "field_type", "locked"]
    only_superuser = True

    delete_permission = False
