# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

import django
from django.core.exceptions import FieldDoesNotExist
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.db.models import Q, ManyToManyField
from django.utils.translation import ugettext as _
from django.views.generic import ListView
from django.http import JsonResponse

from django_webix.views.generic.base import WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin

try:
    from django.contrib.gis.geos import GEOSGeometry
except ImportError:
    GEOSGeometry = object

try:
    from django.contrib.gis.geos import MultiPolygon
except ImportError:
    MultiPolygon = object


class WebixListView(WebixBaseMixin,
                    WebixPermissionsMixin,
                    WebixUrlMixin,
                    ListView):
    # request vars
    http_method_names = ['get', 'post']  # enable POST for filter porpouse

    # queryset vars
    pk_field = None
    fields = None  # ex. [{'field_name':'XXX','datalist_column':'YYY',}]
    # paging
    enable_json_loading = False
    paginate_count_default = 100
    paginate_start_default = 0
    paginate_count_key = 'count'
    paginate_start_key = 'start'

    # template vars
    template_name = 'django_webix/generic/list.js'
    title = None
    actions_style = None
    enable_column_copy = True
    enable_column_delete = True
    enable_row_click = True
    type_row_click = 'single'  # or 'double'
    enable_actions = True

    ########### QUERYSET BUILDER ###########

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

    def _elaborate_qsets_filters(self, data):

        if 'qsets' in data and 'operator' in data:
            operator = data.get('operator')
            if len(data.get('qsets'))==0: # BYPASS
                qset = Q()
            for j, data_qset in enumerate(data.get('qsets')):
                if 'operator' in data_qset:
                    qset_to_applicate = self._elaborate_qsets_filters(data_qset)
                else:
                    qset_to_applicate = Q(**{data_qset.get('path'): data_qset.get('val')})
                if j == 0:
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
            #try:
                return self._elaborate_qsets_filters(filters)
            #except:
            #    print(_('ERROR: qsets structure is incorrect'))
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
                    print(_('ERROR: geo srid is incorrect'))
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
                print(_('ERROR: geo filter is incorrect'))
        return None  # by default filters are not set

    def get_sql_filters(self, request):
        filters = self._decode_text_filters(request, 'sql_filters')
        if filters is not None:
            return filters
        # by default filters are not set
        return None

    def _optimize_select_related(self, qs):
        # Estrapolo le informazione per popolare `select_related`
        _select_related = []
        if self.get_fields() is not None:
            for field in self.get_fields():
                if field.get('field_name') is not None:
                    field_name = field.get('field_name')
                    _model = self.model
                    _field = None
                    _related = []
                    for name in field_name.split('__'):
                        try:
                            _field = _model._meta.get_field(name)
                            if isinstance(_field, ManyToManyField):  # Check if field is M2M
                                raise FieldDoesNotExist()
                        except FieldDoesNotExist:
                            break  # name is probably a lookup or transform such as __contains
                        if hasattr(_field, 'related_model') and _field.related_model is not None:
                            _related.append(name)
                            _model = _field.related_model  # field is a relation
                        else:
                            break  # field is not a relation, any name that follows is probably a lookup or transform
                    _related = '__'.join(_related)
                    if _related != '':
                        _select_related.append(_related)
            qs = qs.select_related(*_select_related)
        return qs

    def get_fields(self):
        return self.fields

    def get_queryset(self, initial_queryset=None):
        # bypass improperly configured for custom queryset without model
        if self.model:
            if initial_queryset is None:
                qs = super(WebixListView, self).get_queryset()
            else:
                qs = initial_queryset
            # apply qsets filters
            if self.qsets_filters is not None:
                qs = qs.filter(self.qsets_filters)
            # apply geo filter
            if self.geo_filter is not None:
                qs = qs.filter(self.geo_filter)
            # apply SQL raw: this is shit! but need for old SW (remove for future)
            if self.sql_filters is not None:
                sql_filter = ' OR '.join(['({sql})'.format(sql=_sql) for _sql in self.sql_filters])
                qs = qs.extra(where=[sql_filter])
            # optimize select related queryset (only if fields are defined)
            qs = self._optimize_select_related(qs)  # TODO
            return qs

        return None

    def get_ordering(self):
        return (self.get_pk_field(),) # TODO

    def apply_ordering(self, queryset):
        # TODO
        #                for field in ordering:
        #                    if field.startswith("-"):
        #                        self._ordering.append({'sort[id]': field[1:], 'sort[dir]': 'desc'})
        #                    else:
        #                        self._ordering.append({'sort[id]': field, 'sort[dir]': 'asc'})
        order = self.get_ordering()
        return queryset.order_by(*order)

    def get_paginate_count(self):
        paginate_count = self.request.GET.get(self.paginate_count_key,
                                    self.request.POST.get(self.paginate_count_key,
                                                          self.paginate_count_default))
        try:
            return int(paginate_count)
        except ValueError:
            raise Exception(_('Paginate count is not integer'))

    def get_paginate_start(self):
        paginate_start = self.request.GET.get(self.paginate_start_key,
                                    self.request.POST.get(self.paginate_start_key,
                                                          self.paginate_start_default))
        try:
            return int(paginate_start)
        except ValueError:
            raise Exception(_('Paginate start is not integer'))

    def paginate_queryset(self, queryset):
        paginate_count = self.get_paginate_count()
        paginate_start = self.get_paginate_start()
        return queryset[paginate_start: paginate_start+paginate_count]

    def _get_objects_datatable_values(self, qs):
        values = [self.get_pk_field()]
        fields = self.get_fields()
        if fields is not None:
            for field in fields:
                if field.get('field_name') is not None and \
                    (field.get('queryset_exclude') is None or field.get('queryset_exclude') != True):
                    values.append(field['field_name'])
        data = qs.values(*values)
        return data

    def get_objects_datatable(self):
        if self.model and not self.enable_json_loading:
            qs = self.get_queryset()
            # filters application (like IDS selections)
            qs = self.filters_objects_datatable(qs)
            # pagination (applied only for json request)
            #if self.is_json_request:
            #    qs = self.paginate_queryset(qs)
            # build output
            if qs is not None:
                if type(qs) == list:
                    return qs
                else: # queryset
                    # apply ordering
                    qs = self.apply_ordering(qs)
                    return self._get_objects_datatable_values(qs)
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

    ########### TEMPLATE BUILDER ###########

    def get_actions_style(self):
        _actions_style = None
        if self.actions_style is None:
            _actions_style = 'select'
        elif self.actions_style in ['buttons' or 'select']:
            _actions_style = self.actions_style
        else:
            raise ImproperlyConfigured(_(
                "Actions style is improperly configured"
                " only options are 'buttons' or 'select' (select by default)."))
        return _actions_style

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

    def get_title(self):
        if self.title is not None:
            return self.title
        if self.model is not None:
            return self.model._meta.verbose_name
        return None

    ########### RESPONSE BUILDER ###########

    @property
    def is_json_request(self):
        if 'json' in self.request.GET or 'json' in self.request.POST:
            return True
        else:
            return False

    def post(self, request, *args, **kwargs):  # all post works like get
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(WebixListView, self).get(request, *args, **kwargs)

    def json_response(self, request, *args, **kwargs):  # TODO
        # ONLY for get_queryset() -> qs and not get_queryset() -> list
        _data = []
        total_count = 0
        if self.model:
            qs = self.get_queryset()
            # filters application (like IDS selections)
            qs = self.filters_objects_datatable(qs)
            # apply ordering
            qs = self.apply_ordering(qs)
            # total count
            total_count = qs.count()
            # apply pagination
            qs_paginate = self.paginate_queryset(qs)
            # build output
            if qs_paginate is not None:
                if type(qs_paginate) == list:
                    raise Exception(
                        _('Json response is available only if get_queryset() return a queryset and not a list'))
                else:  # queryset
                    _data = self._get_objects_datatable_values(qs_paginate)

        # output must be list and not values of queryset
        data = {
            "count": self.get_paginate_count(),
            "total_count": total_count,
            "pos": self.get_paginate_start(),
            "data": list(_data)
        }
        return JsonResponse(data, safe=False)

    def dispatch(self, *args, **kwargs):

        self.qsets_filters = self.get_qsets_filters(self.request)

        self.geo_filter = self.get_geo_filter(self.request)

        self.sql_filters = self.get_sql_filters(self.request)  # this is shit! but need for old SW (remove for future)

        if not self.has_view_permission(request=self.request):
            raise PermissionDenied(_('View permission is not allowed'))

        if self.is_json_request:  # added for json response with paging
            return self.json_response(self.request, *args, **kwargs)
        else:  # standard response with js webix template structure
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
            # paging
            'is_json_loading': self.enable_json_loading,
            'paginate_count_default': self.paginate_count_default,
            'paginate_count_key': self.paginate_count_key,
            'paginate_start_key': self.paginate_start_key,
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
        raise ImproperlyConfigured(_("Generic TemplateListView needs to define data for datatable"))
