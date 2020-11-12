# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

import django
from django.db.models import Q
from django.utils.translation import ugettext as _


try:
    from django.contrib.gis.geos import GEOSGeometry
except ImportError:
    GEOSGeometry = object

try:
    from django.contrib.gis.geos import MultiPolygon
except ImportError:
    MultiPolygon = object


def decode_text_filters(request, key):
    if request.method == 'GET':
        filters_text = request.GET.get(key, None)
    elif request.method == 'POST':
        filters_text = request.POST.get(key, None)
    else:
        filters_text = None

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


def from_geo_dict_to_qset(model, data):
    if issubclass(GEOSGeometry, django.contrib.gis.geos.GEOSGeometry) and \
        issubclass(MultiPolygon, django.contrib.gis.geos.GEOSGeometry):
        if 'geo_field_name' in data and 'polygons_srid' in data and 'polygons' in data:
            geo_field_name = data.get('geo_field_name')
            polygons = []
            for geo_text in data['polygons']:
                polygons.append(GEOSGeometry(geo_text))
            geo = MultiPolygon(polygons)
            try:
                geo.srid = int(data.get('polygons_srid'))
            except ValueError:
                print(_('ERROR: geo srid is incorrect'))
            geo_field = model._meta.get_field(geo_field_name)
            _geo = geo.transform(geo_field.srid, clone=True).buffer(
                0)  # se l'unione del multipolygon risultasse invalida
            qset = Q(**{geo_field_name + '__within': _geo})
        else:
            qset = Q()
        return qset
    return Q()


def from_dict_to_qset(data):
    if 'qsets' in data and 'operator' in data:
        operator = data.get('operator')
        negate = data.get('negate', False)
        if len(data.get('qsets')) == 0:  # BYPASS
            qset = Q()
        for j, data_qset in enumerate(data.get('qsets')):
            if 'operator' in data_qset:
                qset_to_applicate = from_dict_to_qset(data_qset)
            else:
                if data_qset.get('path').endswith("__exact_in"):
                    data_qset['path'] = data_qset['path'].replace("__exact_in", "__in")
                    data_qset['val'] = data_qset['val'].split(",")
                qset_to_applicate = Q(**{data_qset.get('path'): data_qset.get('val')})
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
