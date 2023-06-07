import django
from django.contrib.postgres import fields
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models


matches = {
    # devono avere questa struttura cioe tutti i dizzonari devono avere operators / input / values
    # ########### Bool
    models.BooleanField: {
        "operators": ["exact", "isnull"],
        "input": "select",
        "values": {'True': 'Yes', 'False': 'No'}
    },
    models.NullBooleanField: {
        "operators": ["exact", "isnull"],
        "input": "select",
        "values": {'True': 'Yes', 'False': 'No'}
    },

    # ####################### number field
    models.AutoField: {
        "operators": ['exact', "isnull", 'gt', 'gte', 'lt', 'lte', 'in'],
        "webix_type": 'integer'
    },
    models.IntegerField: {
        "operators": ['exact', "isnull", 'gt', 'gte', 'lt', 'lte', 'in'],
        "webix_type": 'integer'
    },
    models.SmallIntegerField: {
        "operators": ['exact', "isnull", 'gt', 'gte', 'lt', 'lte', 'in'],
        "webix_type": 'integer'
    },
    models.PositiveSmallIntegerField: {
        "operators": ['exact', "isnull", 'gt', 'gte', 'lt', 'lte', 'in'],
        "webix_type": 'integer'
    },
    models.PositiveIntegerField: {
        "operators": ['exact', "isnull", 'gt', 'gte', 'lt', 'lte', 'in'],
        "webix_type": 'integer'
    },
    models.BigIntegerField: {
        "operators": ['exact', "isnull", 'gt', 'gte', 'lt', 'lte', 'in'],
        "webix_type": 'integer'
    },
    models.BigAutoField: {
        "operators": ['exact', "isnull", 'gt', 'gte', 'lt', 'lte', 'in'],
        "webix_type": 'integer'
    },

    models.FloatField: {
        "operators": ['exact', "isnull", 'gt', 'gte', 'lt', 'lte', 'in'],
        "webix_type": 'double'
    },
    models.DecimalField: {
        "operators": ['exact', "isnull", 'gt', 'gte', 'lt', 'lte', 'in'],
        "webix_type": 'double'
    },

    # ################ Time field
    models.DateField: {
        "operators": ["exact", "isnull", 'gt', 'gte', 'lt', 'lte', 'range', 'year', 'month', 'day', 'week_day',
                      'week'],
        # 'hour', 'minute', 'second' 'year', 'month', 'day', 'week_day', 'week'
        "webix_type": 'date',
    },
    models.DateTimeField: {
        "operators": ["exact", "isnull", 'gt', 'gte', 'lt', 'lte', 'range', 'year', 'month', 'day', 'week_day', 'week',
                      'hour', 'minute', 'second'],
        # 'hour', 'minute', 'second' 'year', 'month', 'day', 'week_day', 'week'
        "webix_type": 'date',
    },
    models.TimeField: {
        "operators": ["exact", "isnull", 'gt', 'gte', 'lt', 'lte', 'range'],  # 'hour', 'minute', 'second'
        "webix_type": 'time',
    },
    models.DurationField: {
        "operators": ["exact", "isnull"],
    },

    # ############## char field+
    models.CharField: {
        "operators": ['exact', 'isnull', 'iexact', 'contains', 'icontains', 'startswith', 'in',
                      'istartswith', 'endswith', 'iendswith', 'regex', 'iregex'],
    },
    models.UUIDField: {
        "operators": ["exact", "isnull"],
    },
    models.URLField: {
        "operators": ["exact", "isnull", "iexact", 'contains', 'icontains', 'startswith',
                      'istartswith', 'endswith', 'iendswith', 'regex', 'iregex'],
    },
    models.TextField: {
        "operators": ["exact", "isnull", "iexact", 'contains', 'icontains', 'startswith', 'in',
                      'istartswith', 'endswith', 'iendswith', 'regex', 'iregex'],
    },
    models.SlugField: {
        "operators": ["exact", "isnull", "iexact", 'contains', 'icontains', 'startswith', 'in',
                      'istartswith', 'endswith', 'iendswith', 'regex', 'iregex'],
    },
    models.IPAddressField: {
        "operators": ["exact", "isnull", 'contains'],
    },
    models.GenericIPAddressField: {
        "operators": ["exact", "isnull", 'contains'],
    },
    models.FilePathField: {
        "operators": ["exact", "isnull", "iexact", 'contains', 'icontains', 'startswith',
                      'istartswith', 'endswith', 'iendswith', 'regex', 'iregex'],
    },
    models.EmailField: {
        "operators": ["exact", "isnull", "iexact", 'contains', 'icontains', 'startswith',
                      'istartswith', 'endswith', 'iendswith', 'regex', 'iregex'],
    },

    # ################### special field
    models.CommaSeparatedIntegerField: {
        "operators": ["isnull"]  # deprecato
    },
    models.BinaryField: {
        "operators": ["isnull"]
    },
    fields.RangeField: {
        "operators": ["isnull"]
    },
    fields.IntegerRangeField: {
        "operators": ["isnull"]
    },
    # deprecated version 2.2 django
    # fields.FloatRangeField: {
    #     "operators": ["isnull"]
    # },
    fields.DecimalRangeField: {
        "operators": ["isnull"]
    },
    fields.DateTimeRangeField: {
        "operators": ["isnull"]
    },
    fields.DateRangeField: {
        "operators": ["isnull"]
    },
    fields.BigIntegerRangeField: {
        "operators": ["isnull"]
    },
    fields.HStoreField: {
        "operators": ["isnull", 'exact', 'has_key', 'has_keys', 'has_any_keys', 'kesy']
    },
    fields.ArrayField: {
        "operators": ['exact', 'contains', 'contained_by', 'isnull', 'overlap'],
        # ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'in', 'contains', 'icontains', 'isnull', 'contained_by', 'len']
    },

    # GEO FIELDS
    models.PolygonField: {
        "operators": ['within', 'isnull'],
    },
    models.MultiPolygonField: {
        "operators": ['within', 'isnull'],
    },
    models.LineStringField: {
        "operators": ['within', 'isnull'],
    },
    models.MultiLineStringField: {
        "operators": ['within', 'isnull'],
    },
    models.PointField: {
        "operators": ['within', 'isnull'],
    },
    models.MultiPointField: {
        "operators": ['within', 'isnull'],
    },
    models.GeometryCollectionField: {
        "operators": ['within', 'isnull'],
    },
}


matches[models.JSONField] = {
    "operators": ["isnull", 'exact', 'has_key', 'has_keys', 'has_any_keys']
}


counter_operator = {
    # 'isnull': 'isnotnull'
}

operators_override = {
    'exact': {'label': '=='}, 'iexact': {}, 'gt': {'label': '>'}, 'gte': {'label': '>='}, 'lt': {'label': '<'},
    'lte': {'label': '<='}, 'contains': {}, 'icontains': {},
    'year': {}, 'month': {}, 'day': {}, 'week_day': {}, 'week': {}, 'hour': {}, 'minute': {}, 'second': {},

    'range': {'nb_inputs': 2},
    'isnull': {"values": {'True': 'Yes', 'False': 'No'}},
    'contained_by': {}, 'len': {}, 'has_key': {}, 'kesy': {},

    'startswith': {}, 'istartswith': {}, 'endswith': {}, 'iendswith': {}, 'regex': {}, 'iregex': {},

    'in': {'multiple': True},
    'has_keys': {'multiple': True},
    'has_any_keys': {'multiple': True},
    'keys': {'multiple': True},
    'overlap': {'multiple': True, 'label': _('Overlap')},

    'within': {'label': _('Contained by'), 'pick_geometry': True},
}
