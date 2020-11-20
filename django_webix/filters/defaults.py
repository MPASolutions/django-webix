from django.db.models import Q

from django_webix.utils.filters import from_dict_to_qset, decode_text_filters
from django_webix_filter.models import WebixFilter
from django_webix_filter.utils.json_converter import get_JSON_for_DB
from filtermerger import RequestFilter


class DjangoBaseLockedWebixFilter(RequestFilter):
    def filter_queryset(self, queryset, **kwargs):
        locked_filters = self.get_param('locked_filters')
        locked_filters_dict = decode_text_filters(locked_filters)
        locked_qset = from_dict_to_qset(locked_filters_dict)
        return queryset.filter(locked_qset)

class DjangoBaseWebixFilter(RequestFilter):
    def filter_queryset(self, queryset, **kwargs):
        filters = self.get_param('filters')
        filters_dict = decode_text_filters(filters)
        qset = from_dict_to_qset(filters_dict)
        return queryset.filter(qset)

class DjangoBaseSqlFilter(RequestFilter):
    def filter_queryset(self, queryset, **kwargs):
        sql_filters = self.get_param('sql_filters')
        sql_filters_dict = decode_text_filters(sql_filters)
        sql_filter_where = ' OR '.join(['({sql})'.format(sql=_sql) for _sql in sql_filters_dict])
        return queryset.extra(where=[sql_filter_where])
