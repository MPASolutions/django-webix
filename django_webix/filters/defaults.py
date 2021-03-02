# -*- coding: utf-8 -*-

from django_filtersmerger import RequestFilter
from django_webix.utils.filters import from_dict_to_qset, decode_text_filters


class DjangoBaseLockedWebixFilter(RequestFilter):
    PARAM = 'locked'

    def filter_queryset(self, queryset, **kwargs):
        locked_filters = self.get_param(self.PARAM)
        if locked_filters not in [None, '']:
            locked_filters_dict = decode_text_filters(locked_filters)
            locked_qset = from_dict_to_qset(locked_filters_dict, model=queryset.model)
            return queryset.filter(locked_qset)
        else:
            return queryset


class DjangoBaseWebixFilter(RequestFilter):
    PARAM = 'filters'

    def filter_queryset(self, queryset, **kwargs):
        filters = self.get_param(self.PARAM)
        if filters not in [None, '']:
            filters_dict = decode_text_filters(filters)
            qset = from_dict_to_qset(filters_dict, model=queryset.model)
            return queryset.filter(qset)
        else:
            return queryset


class DjangoBaseSqlFilter(RequestFilter):
    PARAM = 'sql'

    def filter_queryset(self, queryset, **kwargs):
        sql_filters = self.get_param(self.PARAM)
        if sql_filters not in [None, '']:
            sql_filters_dict = decode_text_filters(sql_filters)
            sql_filter_where = ' OR '.join(['({sql})'.format(sql=_sql) for _sql in sql_filters_dict])
            return queryset.extra(where=[sql_filter_where])
        else:
            return queryset
