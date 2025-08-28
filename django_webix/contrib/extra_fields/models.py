import django_webix.contrib.extra_fields.signals  # noqa: F401
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_webix.contrib.extra_fields.fields import NotDbColumnField

try:
    from django_dal.models import DALModel as Model
except ImportError:
    from django.db.models import Model


def get_ct_models_with_extra_fields():
    from django_webix.contrib.extra_fields.models_mixin import ExtraFieldsModel

    ct_models = []
    for model in apps.get_models():
        if issubclass(model, ExtraFieldsModel):
            ct_model = ContentType.objects.get_for_model(model)
            ct_models.append(ct_model)
    return ct_models


class ModelField(Model):
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("Model"),
        on_delete=models.CASCADE,
        # problem for import partially inizialized module
        # limit_choices_to={'id__in':[i.pk for i in get_ct_models_with_extra_fields()]}
    )
    label = models.CharField(_("Description"), max_length=255)
    field_name = models.CharField(
        _("Field name"),
        max_length=64,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z]+[\w-]*$",
                message=_("Field name must not contain spaces and special characters, and must begin with a letter"),
            ),
        ],
    )
    field_type = models.CharField(
        _("Field type"),
        max_length=64,
        choices=[
            (_field, _field.upper())
            for _field in [
                "IntegerField",
                "FloatField",
                "BooleanField",
                "CharField",
                "DateField",
                # 'ChoiceField',
                # 'ForeignKey',
            ]
        ],
    )
    # TODO max and min
    related_to = models.ForeignKey(
        ContentType,
        verbose_name=_("Model for FK"),
        on_delete=models.CASCADE,
        related_name="extra_fields_related_to",
        blank=True,
        null=True,
    )
    locked = models.BooleanField(_("Locked"), blank=True, default=False)

    class Meta:
        verbose_name = _("Model field")
        verbose_name_plural = _("Model fields")
        unique_together = [("content_type", "field_name")]

    def __str__(self):
        return self.label

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            field = self.content_type.model_class()._meta.get_field(self.field_name)
        except FieldDoesNotExist:
            field = None
        if field is not None and not isinstance(field, NotDbColumnField):
            raise Exception("Error: this field name is already present into model")
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class ModelFieldChoice(Model):
    model_field = models.ForeignKey(ModelField, verbose_name=_("Model field"), on_delete=models.CASCADE)

    key = models.TextField(verbose_name=_("Key"), blank=True)
    value = models.TextField(verbose_name=_("Value"), blank=True)

    class Meta:
        verbose_name = _("Model field choice")
        verbose_name_plural = _("Model fields choices")
        unique_together = [("model_field", "key")]

    def __str__(self):
        return "{}: {}".format(self.model_field, self.value)


class ModelFieldValue(Model):
    # field
    model_field = models.ForeignKey(ModelField, verbose_name=_("Model field"), on_delete=models.CASCADE)
    # instance
    content_type = models.ForeignKey(ContentType, verbose_name=_("Content type"), on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(verbose_name=_("Object ID"), db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")
    # value
    value = models.TextField(verbose_name=_("Value"), blank=True)
    # extra
    locked = models.BooleanField(_("Locked"), blank=True, default=False)

    class Meta:
        verbose_name = _("Model field value")
        verbose_name_plural = _("Model fields values")
        unique_together = [("content_type", "object_id", "model_field")]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["content_type", "object_id", "model_field"]),
        ]

    def __str__(self):
        return "{}: {}".format(self.content_object, self.model_field.label)
