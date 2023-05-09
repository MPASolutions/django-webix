import datetime
import json

import django
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import Q, DateTimeField
from django.db.models.fields.reverse_related import ForeignObjectRel

try:
    import psycopg2
except ModuleNotFoundError:
    ArrayField = None
else:
    from django.contrib.postgres.fields import ArrayField

try:
    from django.contrib.gis.geos import GEOSGeometry
except ImportError:
    GEOSGeometry = object

try:
    from django.contrib.gis.geos import MultiPolygon
except ImportError:
    MultiPolygon = object


def decode_text_filters(filters_text):
    filters = None
    if filters_text is not None:
        if type(filters_text) == str:
            # NB: JSON syntax is not Python syntax. JSON requires double quotes for its strings.
            try:
                filters = json.loads(filters_text)
            except json.JSONDecodeError:
                filters = None
        elif type(filters_text) == dict:
            filters = filters_text
        else:
            filters = None
    return filters  # by default filters are not set


def from_dict_to_qset(data, model):
    if 'qsets' in data and 'operator' in data:
        operator = data.get('operator')
        negate = data.get('negate', False)
        if len(data.get('qsets')) == 0:  # BYPASS
            qset = Q()
        for j, data_qset in enumerate(data.get('qsets')):
            if 'operator' in data_qset:
                qset_to_applicate = from_dict_to_qset(data_qset, model=model)
            else:
                # search field type for filer applied
                _curr_model = model
                _curr_field = None

                for _field in data_qset.get('path').split("__")[:-1]:
                    try:
                        _curr_field = _curr_model._meta.get_field(_field)
                    except FieldDoesNotExist:
                        _curr_model = None
                        _curr_field = None
                    else:
                        if issubclass(type(_curr_field), models.ForeignKey):
                            _curr_model = _curr_field.remote_field.get_related_field().model
                        elif issubclass(type(_curr_field), ForeignObjectRel):
                            _curr_model = _curr_field.related_model
                        elif issubclass(type(_curr_field), models.ManyToManyField):
                            _curr_model = _curr_field.remote_field.get_related_field().model
                        elif issubclass(type(_curr_field), django.contrib.contenttypes.fields.GenericRelation):
                            _curr_model = _curr_field.related_model
                        else:
                            pass  # there are no others field

                # its an array so put in into array
                if ArrayField and isinstance(_curr_field, ArrayField) and not isinstance(data_qset['val'], list):
                    data_qset['val'] = [data_qset.get('val')]

                # 2 type of value for operator range, from WebixList is a dict and from AdvanceFilter is a list
                if data_qset.get('path').endswith("__range") and isinstance(data_qset.get('val'), dict):
                    # {"start":null,"end":null}
                    val = data_qset.get('val')
                    base_path = data_qset.get('path').replace('__range', '')
                    qset_to_applicate = Q()
                    if val is not None and val.get('start') is not None:
                        qset_to_applicate = Q(**{base_path + '__gte': parse(val.get('start'))})
                    if val is not None and val.get('end') is not None:
                        data_end = parse(val.get('end'))
                        if isinstance(_curr_field, DateTimeField) and \
                            datetime.datetime.combine(data_end.date(), datetime.datetime.min.time()) == data_end:
                            data_end += relativedelta(days=1)
                        qset_to_applicate &= Q(**{base_path + '__lte': data_end})
                elif data_qset.get('path').endswith("__exact_in"):
                    data_qset['path'] = data_qset['path'].replace("__exact_in", "__in")
                    data_qset['val'] = data_qset['val'].split(",")
                    qset_to_applicate = Q(**{data_qset.get('path'): data_qset.get('val')})
                else:
                    valore_query = data_qset.get('val')
                    if isinstance(_curr_field, models.BooleanField) or \
                        isinstance(_curr_field, models.NullBooleanField) or \
                        data_qset.get('path').endswith("__isnull"):
                        # force cast
                        if valore_query.lower() == 'false':
                            valore_query = False
                        else:
                            valore_query = True
                    qset_to_applicate = Q(**{data_qset.get('path'): valore_query})
            if j == 0:
                qset = qset_to_applicate
            else:
                if operator == 'AND':
                    qset = qset & qset_to_applicate
                elif operator == 'OR':
                    qset = qset | qset_to_applicate
        if negate is True:
            qset = ~Q(qset)
    elif 'path' in data and 'val' in data:
        if data.get('path').endswith("__exact_in"):
            data['path'] = data['path'].replace("__exact_in", "__in")
            data['val'] = data['val'].split(",")
        qset = Q(**{data.get('path'): data.get('val')})
    else:
        qset = Q()
    return qset


def combo_with_icontains_filter(combo_widget):
    if 'options' not in combo_widget:
        return combo_widget

    options_data = combo_widget['options']
    combo_widget.update({
        'view':'combo',
        'options': {
            'filter': 'filter_icontains',
            'body': {
                'data': options_data
            }
        }
    })
    return combo_widget
