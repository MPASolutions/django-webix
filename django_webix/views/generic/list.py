# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

import django
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.views.generic import ListView

try:
    from django.contrib.gis.geos import GEOSGeometry
except ImportError:
    GEOSGeometry = object

try:
    from django.contrib.gis.geos import MultiPolygon
except ImportError:
    MultiPolygon = object

from django_webix.views.generic.base import WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin


class WebixListView(WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin, ListView):
    http_method_names = ['get', 'post']  # enable POST for filter porpouse

    # defaults and init
    template_name = 'django_webix/generic/list.js'
    pk_field = None
    title = None
    actions_style = None
    enable_column_copy = True
    enable_column_delete = True
    enable_row_click = True
    type_row_click = 'single'  # or 'double'
    enable_actions = True
    fields = None  # ex. [{'field_name':'XXX','datalist_column':'YYY',}]

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.qsets_filters = self.get_qsets_filters(request)
        self.geo_filter = self.get_geo_filter(request)
        self.sql_filters = self.get_sql_filters(request)  # this is shit! but need for old SW (remove for future)
        return super(WebixListView, self).get(request, *args, **kwargs)

    # {
    #     'operator': 'AND', # by default
    #     'qsets':[
    #         {'sql': '...'}
    #         {'path': 'appezzamento__superficie__in','val': [1,2],}
    #         {'geo_field_name': '...','geo_srid': '...','polygons':'...'}
    #     ]
    # }
    def _decode_text_filters(self, request, key):
        if request.method == 'GET':
            filters_text = request.GET.get(key, None)
        elif request.method == 'POST':
            filters_text = request.POST.get(key, None)
        else:
            filters_text = None

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

            if filters is not None:
                return filters
        return None  # by default filters are not set

    def _elaborate_qsets_filters(self, data):
        if 'qsets' in data and 'operator' in data:
            operator = data.get('operator')
            for j, data_qset in enumerate(data.get('qsets')):
                if 'operator' in data_qset:
                    qset_to_applicate = self._elaborate_qset(data_qset)
                else:
                    qset_to_applicate = Q(**{data_qset.get('path'): data_qset.get('val')})
                if j == 1:
                    qset = qset_to_applicate
                else:
                    if operator == 'AND':
                        qset = qset & qset_to_applicate
                    elif operator == 'OR':
                        qset = qset & qset_to_applicate
        elif 'path' in data and 'val' in data:
            qset = Q(**{data.get('path'): data.get('val')})
        else:
            qset = Q()
        return qset

    def get_qsets_filters(self, request):
        filters = self._decode_text_filters(request, 'filters')
        if filters is not None:
            try:
                return self._elaborate_qsets_filters(filters)
            except:
                print('ERROR: qsets structure is incorrect')
        return None  # by default filters are not set

    def _elaborate_geo_filter(self, data):
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
                    print('ERROR: geo srid is incorrect')
                geo_field = self.model._meta.get_field(geo_field_name)
                _geo = geo.transform(geo_field.srid, clone=True)
                qset = Q(**{geo_field_name + '__intersects': _geo})
            else:
                qset = Q()
            return qset
        return Q()

    def get_geo_filter(self, request):
        filters = self._decode_text_filters(request, 'geo_filters')
        if filters is not None:
            try:
                return self._elaborate_geo_filter(filters)
            except:
                print('ERROR: geo filter is incorrect')
        return None  # by default filters are not set

    def get_sql_filters(self, request):
        filters = self._decode_text_filters(request, 'sql_filters')
        if filters is not None:
            return filters
        # by default filters are not set
        return None

    def get_actions_style(self):
        _actions_style = None
        if self.actions_style is None:
            _actions_style = 'select'
        elif self.actions_style in ['buttons' or 'select']:
            _actions_style = self.actions_style
        else:
            raise ImproperlyConfigured(
                "Actions style is improperly configured"
                " only options are 'buttons' or 'select' (select by default).")
        return _actions_style

    def get_title(self):
        if self.title is not None:
            return self.title
        if self.model is not None:
            return self.model._meta.verbose_name
        return None

    def is_enable_actions(self, request):
        return self.enable_actions

    def is_enable_column_copy(self, request):
        return self.enable_column_copy

    def is_enable_column_delete(self, request):
        return self.enable_column_delete

    def is_enable_row_click(self, request):
        return self.enable_row_click

    def get_type_row_click(self, request):
        return self.type_row_click

    def get_fields(self):
        return self.fields

    def get_queryset(self):
        # bypass improperly configured for custom queryset without model
        if self.model:
            qs = super(WebixListView, self).get_queryset()
            # apply qsets filters
            if self.qsets_filters is not None:
                qs = qs.filter(self.qsets_filters)
            # apply geo filter
            if self.geo_filter is not None:
                qs = qs.filter(self.geo_filter)
            # applay SQL raw: this is shit! but need for old SW (remove for future)
            if self.sql_filters is not None:
                sql_filter = ' OR '.join(['({sql})'.format(sql=_sql) for _sql in self.sql_filters])
                qs = qs.extra(where=[sql_filter])
            return qs
        return None

    def get_objects_datatable(self):
        if self.model:
            qs = self.get_queryset()
            # filters application (like IDS selections)
            qs = self.filters_objects_datatable(qs)
            # build output
            if qs is not None:
                if type(qs) == list:
                    return qs
                else:  # queryset
                    values = [self.get_pk_field()]
                    fields = self.get_fields()
                    if fields is not None:
                        for field in fields:
                            if field.get('field_name') is not None and \
                                (field.get('queryset_exclude') is None or field.get('queryset_exclude') != True):
                                values.append(field['field_name'])
                    data = qs.values(*values)
                    return data
        return None

    def filters_objects_datatable(self, qs):
        ids = self.request.POST.get('ids', '').split(',')
        ids = list(set(ids) - set([None, '']))

        if len(ids) > 0:
            if type(qs) == list:
                for item in qs:
                    if item.get('id') not in ids:
                        qs.pop(item)
            else:
                auto_field_name = self.model._meta.auto_field.name
                qs = qs.filter(**{auto_field_name + '__in': ids})
        return qs

    def get_pk_field(self):
        if self.pk_field is not None:
            return self.pk_field
        return 'id'

    def dispatch(self, *args, **kwargs):
        if not self.has_view_permission(request=self.request):
            raise PermissionDenied(_('View permission is not allowed'))
        return super(WebixListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WebixListView, self).get_context_data(**kwargs)
        self.object = None  # bypass for mixin permissions functions
        context.update(self.get_context_data_webix_permissions(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_url(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_base(request=self.request))
        context.update({
            'fields': self.get_fields(),
            'get_pk_field': self.get_pk_field(),
            'objects_datatable': self.get_objects_datatable(),
            'is_enable_column_copy': self.is_enable_column_copy(self.request),
            'is_enable_column_delete': self.is_enable_column_delete(self.request),
            'is_enable_row_click': self.is_enable_row_click(self.request),
            'type_row_click': self.get_type_row_click(self.request),
            'is_enable_actions': self.is_enable_actions(self.request),
            'actions_style': self.get_actions_style(),
            'title': self.get_title(),
            # extra filters
            'is_filters_active': self.qsets_filters is not None,
            'is_geo_filter_active': self.geo_filter is not None,
            'is_sql_filters_active': self.sql_filters is not None,
        })
        return context


class WebixTemplateListView(WebixListView):
    model = None
    enable_column_copy = False
    enable_column_delete = False
    add_permission = False
    change_permission = False
    delete_permission = False
    view_permission = True
    remove_disabled_buttons = True
    enable_row_click = False

    def get_objects_datatable(self):
        raise ImproperlyConfigured("Generic TemplateListView needs to define data for datatable")

# # -*- coding: utf-8 -*-
#
# import dateutil
# import re
# from django.core.exceptions import FieldDoesNotExist
# from django.core.exceptions import ImproperlyConfigured
# from django.db.models import fields, ManyToManyField
# from django.db.models.query import QuerySet
# from django.http import JsonResponse
# from django.views.generic import View
#
#
# # TODO: Spostare in django-webix con crazione liste automatiche
# class WebixJsonListView(View):
#     http_method_names = ['get', 'head', 'options', 'trace']
#     queryset = None
#     model = None
#     ordering = None
#
#     list_display = ()
#     list_filter = ()
#     list_per_page = 100
#     actions = []
#
#     def __init__(self, **kwargs):
#         super().__init__()
#         self._filters = []  # JSON filters
#         self._ordering = []  # JSON ordering
#
#     def get_queryset(self):
#         if self.queryset is not None:
#             queryset = self.queryset
#             if isinstance(queryset, QuerySet):
#                 queryset = queryset.all()
#         elif self.model is not None:
#             queryset = self.model._default_manager.all()
#         else:
#             raise ImproperlyConfigured(
#                 "%(cls)s is missing a QuerySet. Define "
#                 "%(cls)s.model, %(cls)s.queryset, or override "
#                 "%(cls)s.get_queryset()." % {
#                     'cls': self.__class__.__name__
#                 }
#             )
#         ordering = self.get_ordering()
#         if ordering:
#             if isinstance(ordering, str):
#                 ordering = (ordering,)
#             queryset = queryset.order_by(*ordering)
#             for field in ordering:
#                 if field.startswith("-"):
#                     self._ordering.append({'sort[id]': field[1:], 'sort[dir]': 'desc'})
#                 else:
#                     self._ordering.append({'sort[id]': field, 'sort[dir]': 'asc'})
#
#         return queryset
#
#     def get_ordering(self):
#         return self.ordering
#
#     def get_context_data(self, **kwargs):
#         qs = self.get_queryset()
#
#         # Estrapolo le informazione per popolare `select_related`
#         _select_related = []
#         for field_name in self.list_display:
#             _model = self.model
#             _field = None
#             _related = []
#             for name in field_name.split('__'):
#                 try:
#                     _field = _model._meta.get_field(name)
#                     if isinstance(_field, ManyToManyField):  # Check if field is M2M
#                         raise FieldDoesNotExist()
#                 except FieldDoesNotExist:
#                     break  # name is probably a lookup or transform such as __contains
#                 if hasattr(_field, 'related_model') and _field.related_model is not None:
#                     _related.append(name)
#                     _model = _field.related_model  # field is a relation
#                 else:
#                     break  # field is not a relation, any name that follows is probably a lookup or transform
#             _related = '__'.join(_related)
#             if _related != '':
#                 _select_related.append(_related)
#         qs = qs.select_related(*_select_related)
#
#         # Applico i filtri passati nella richiesta
#         for field_name in self.list_display:
#             # Estrapolo i valori del filtro e il tipo di filtro se presente
#             values = [(
#                 value,
#                 re.findall('^filter\[.*?\]\[(.*?)\]$|$', field)[0] or None
#             ) for field, value in self.request.GET.items() if
#                 field.startswith('filter[{}]'.format(field_name)) and value not in [None, '', False]
#             ]
#
#             if len(values) == 0:
#                 continue  # Nessun filtro richiesto, passo al successivo
#
#             # Recupero il field seguendo le fks
#             _model = self.model
#             _field = None
#             for name in field_name.split('__'):
#                 try:
#                     _field = _model._meta.get_field(name)
#                 except FieldDoesNotExist:
#                     break  # name is probably a lookup or transform such as __contains
#                 if hasattr(_field, 'related_model') and _field.related_model is not None:
#                     _model = _field.related_model  # field is a relation
#                 else:
#                     break  # field is not a relation, any name that follows is probably a lookup or transform
#             if _field is None:
#                 continue  # Passo al filtro successivo
#             field_type = _field.get_internal_type()
#
#             # Creo le liste delle tipologie dei fields
#             integers = list(map(
#                 lambda x: x().get_internal_type(),
#                 [fields.IntegerField, fields.BigIntegerField, fields.SmallIntegerField, fields.PositiveIntegerField,
#                  fields.PositiveSmallIntegerField, fields.AutoField, fields.BigAutoField]
#             ))
#             reals = list(map(lambda x: x().get_internal_type(), [fields.FloatField, fields.DecimalField]))
#             bools = list(map(lambda x: x().get_internal_type(), [fields.BooleanField, fields.NullBooleanField]))
#
#             # Creo le varie regex
#             if field_type in integers:
#                 regex = r'([<>]=?)?\s*([+-]?[0-9]+)+'  # Regex for <,>,<=,>= and integer number
#             elif field_type in reals:
#                 regex = r'([<>]=?)?\s*([+-]?[0-9]*[.]?[0-9]+)+'  # Regex for <,>,<=,>= and float number (e.g. 3.14)
#
#             # Filtro i dati secondo i valori passati
#             # Nota: possono esserci più valori per un field (per esempio le date hanno start e end)
#             for value, action in values:
#                 # Applico la regola per i numeri
#                 if field_type in integers or field_type in reals:
#                     regexs = re.findall(regex, value)
#                     if len(regexs) > 0:
#                         for regex in regexs:
#                             symbol, number = regex
#                             if symbol == '>':
#                                 qs = qs.filter(**{'{0}__{1}'.format(field_name, 'gt'): number})
#                             elif symbol == '<':
#                                 qs = qs.filter(**{'{0}__{1}'.format(field_name, 'lt'): number})
#                             elif symbol == '>=':
#                                 qs = qs.filter(**{'{0}__{1}'.format(field_name, 'gte'): number})
#                             elif symbol == '<=':
#                                 qs = qs.filter(**{'{0}__{1}'.format(field_name, 'lte'): number})
#                             elif symbol == '=' or symbol == '==':
#                                 qs = qs.filter(**{'{0}__{1}'.format(field_name, 'exact'): number})
#                             elif symbol == '~' or symbol == '~*':
#                                 qs = qs.filter(**{'{0}__{1}'.format(field_name, 'icontains'): number})
#                             else:
#                                 qs = qs.filter(**{'{0}__{1}'.format(field_name, 'exact'): number})
#
#                 # fields.CharField
#                 # fields.BinaryField
#                 # fields.CommaSeparatedIntegerField
#                 # fields.EmailField
#                 # fields.FilePathField
#                 # fields.GenericIPAddressField
#                 # fields.IPAddressField
#                 # fields.SlugField
#                 # fields.TextField
#                 # fields.URLField
#                 # fields.UUIDField
#
#                 # fields.TimeField
#                 # fields.DurationField
#                 # ATTENIZIONE A RANGE DI DATE O TIME
#
#                 elif field_type in list(map(lambda x: x().get_internal_type(), [fields.DateField, fields.DateTimeField, fields.TimeField])):
#                     try:
#                         qs = qs.filter(**{
#                             '{0}__{1}'.format(field_name, 'gte' if action == 'start' else 'lte'): dateutil.parser.parse(value)
#                         })
#                     except Exception as e:
#                         pass
#
#                 # TODO: Aggiungere i filtri mancanti
#
#                 elif field_type in bools:
#                     if value in ['true', 'false']:
#                         qs = qs.filter(**{'{0}'.format(field_name): True if value == 'true' else False})
#                     if value == ['null', 'not_null']:
#                         qs = qs.filter(**{'{0}__{1}'.format(field_name, 'isnull'): True if value == 'null' else False})
#                 else:  # Tutto il resto passa con un icontains
#                     qs = qs.filter(**{'{0}__{1}'.format(field_name, 'icontains'): value})
#
#         # Ordino il QuerySet
#         if self.request.GET.get('sort[id]') not in [None, '', False] and \
#             self.request.GET.get('sort[dir]') not in [None, '', False] and \
#             self.request.GET.get('sort[id]') in self.list_display:
#
#             # Check if ordering by field or method
#             field_path = self.request.GET.get('sort[id]').split('__')
#             model = self.model
#             isvalid = True
#             for elem in field_path:
#                 try:
#                     field = model._meta.get_field(elem)
#                 except FieldDoesNotExist:
#                     isvalid = False
#                     break  # name is probably a lookup or transform such as __contains
#                 if hasattr(field, 'related_model') and field.related_model is not None:
#                     model = field.related_model  # field is a relation
#                 else:
#                     break  # field is not a relation, any name that follows is probably a lookup or transform
#
#             if isvalid and self.request.GET.get('sort[dir]') == 'asc':
#                 qs = qs.order_by(self.request.GET.get('sort[id]'))
#             elif isvalid and self.request.GET.get('sort[dir]') == 'desc':
#                 qs = qs.order_by('-{}'.format(self.request.GET.get('sort[id]')))
#
#             if isvalid:
#                 self._ordering.append({
#                     'sort[id]': self.request.GET.get('sort[id]'),
#                     'sort[dir]': self.request.GET.get('sort[dir]')
#                 })
#
#         # Pagino il QuerySet
#         count = int(self.request.GET.get('count', self.list_per_page))
#         pos = int(self.request.GET.get('start', 0))
#         qs_limited = qs[pos:pos + count]
#
#         # Estrapolo i dati e creo una lista di dizionari
#         data = []
#         for instance in qs_limited:
#             instance_dict = {'id': instance.pk}
#             for field in self.list_display:
#                 field_path = field.split('__')
#                 attr = instance
#                 for index, elem in enumerate(field_path):
#                     # Try to get m2m values joined by comma
#                     try:
#                         if hasattr(attr, '_meta') and hasattr(attr._meta, 'get_field') and \
#                             callable(attr._meta.get_field) and isinstance(attr._meta.get_field(elem), ManyToManyField):
#                             attr = ', '.join(getattr(attr, elem).values_list(
#                                 '__'.join(field_path[index + 1:]),
#                                 flat=True
#                             ).distinct())
#                             break
#                     except FieldDoesNotExist:
#                         pass
#                     # Otherwise get attribute
#                     attr = getattr(attr, elem, None)
#                 if callable(attr):
#                     instance_dict[field] = attr()
#                 else:
#                     instance_dict[field] = attr
#             data.append(instance_dict)
#
#         kwargs.update({
#             'data': data,
#             "count": len(data),
#             "total_count": qs.count(),
#             "pos": pos,
#             # "session": session,
#             # "filters": filters,
#             "ordering": self._ordering
#         })
#         return kwargs
#
#     def get(self, request, *args, **kwargs):
#         context = self.get_context_data(**kwargs)
#         return JsonResponse(context)
