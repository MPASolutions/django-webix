from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Min, Q
from django.db.models.functions import Cast
from itertools import chain
from django.db.models.query_utils import FilteredRelation

from django_webix.contrib.extra_fields.models import ModelField

try:
    from mpadjango.db.models.manager import MpaManager as Manager
    from mpadjango.db.models.query import MpaQuerySet as QuerySet
except ImportError:
    try:
        from django_dal.managers import DALManager as Manager
        from django_dal.query import DALQuerySet as QuerySet
    except ImportError:
        from django.db.models.manager import Manager
        from django.db.models.query import QuerySet


class ExtraFieldsQuerySet(QuerySet):
    def _annotate(self, args, kwargs, select=True):
        self._validate_values_are_expressions(
            args + tuple(kwargs.values()), method_name="annotate"
        )
        annotations = {}
        for arg in args:
            # The default_alias property may raise a TypeError.
            try:
                if arg.default_alias in kwargs:
                    raise ValueError(
                        "The named annotation '%s' conflicts with the "
                        "default name for another annotation." % arg.default_alias
                    )
            except TypeError:
                raise TypeError("Complex annotations require an alias")
            annotations[arg.default_alias] = arg
        annotations.update(kwargs)

        clone = self._chain()
        names = self._fields
        if names is None:
            names = set(
                chain.from_iterable(
                    (field.name, field.attname)
                    if hasattr(field, "attname")
                    else (field.name,)
                    for field in self.model._meta.get_fields()
                )
            )

        for alias, annotation in annotations.items():
            if alias in names:
                if self.model._meta.get_field(alias).concrete == True:
                    raise ValueError(
                        "The annotation '%s' conflicts with a field on "
                        "the model." % alias
                    )
            if isinstance(annotation, FilteredRelation):
                clone.query.add_filtered_relation(annotation, alias)
            else:
                clone.query.add_annotation(
                    annotation,
                    alias,
                    select=select,
                )
        for alias, annotation in clone.query.annotations.items():
            if alias in annotations and annotation.contains_aggregate:
                if clone._fields is None:
                    clone.query.group_by = True
                else:
                    clone.query.set_group_by()
                break

        return clone


def add_extra_fields_to_queryset(queryset):
    # queryset = queryset.select_related('extra_fields')
    for mf in ModelField.objects.filter(content_type=ContentType.objects.get_for_model(queryset.model)):
        field_class = getattr(models, mf.field_type)
        queryset = queryset.annotate(**{mf.field_name: Cast(Min('extra_fields__value',
                                                                filter=Q(extra_fields__model_field_id=int(mf.pk))),
                                                            field_class())
                                        })
    return queryset


class ExtraFieldsManager(Manager.from_queryset(ExtraFieldsQuerySet)):

    def no_extra_fields(self):
        return super().get_queryset()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = add_extra_fields_to_queryset(queryset)
        return queryset
