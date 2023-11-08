from django_webix.contrib.extra_fields.managers import ExtraFieldsManager
from django_webix.contrib.extra_fields.models import ModelFieldValue
from django.contrib.contenttypes.fields import GenericRelation

try:
    from django_dal.models import DALModel as Model
except ImportError:
    from django.db.models import Model


class ExtraFieldsModel(Model):
    objects = ExtraFieldsManager()
    extra_fields = GenericRelation(ModelFieldValue)

    class Meta:
        abstract = True
