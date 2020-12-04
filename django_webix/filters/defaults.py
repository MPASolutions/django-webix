from django.db.models import Q

from django_webix.utils.filters import from_dict_to_qset, decode_text_filters
from django_webix_filter.models import WebixFilter
from django_webix_filter.utils.json_converter import get_JSON_for_DB
from django_filtersmerger import RequestFilter


class DjangoBaseLockedWebixFilter(RequestFilter):
    def filter_queryset(self, queryset, **kwargs):
        locked_filters = self.get_param('locked')
        if locked_filters is not None:
            locked_filters_dict = decode_text_filters(locked_filters)
            locked_qset = from_dict_to_qset(locked_filters_dict)
            return queryset.filter(locked_qset)
        else:
            return queryset

class DjangoBaseWebixFilter(RequestFilter):
    def filter_queryset(self, queryset, **kwargs):
        filters = self.get_param('filters')
        if filters is not None:
            filters_dict = decode_text_filters(filters)
            qset = from_dict_to_qset(filters_dict)
            #raise Exception('test',filters_dict,qset)
            return queryset.filter(qset)
        else:
            return queryset

class DjangoBaseSqlFilter(RequestFilter):
    def filter_queryset(self, queryset, **kwargs):
        sql_filters = self.get_param('sql')
        if sql_filters is not None:
            sql_filters_dict = decode_text_filters(sql_filters)
            sql_filter_where = ' OR '.join(['({sql})'.format(sql=_sql) for _sql in sql_filters_dict])
            return queryset.extra(where=[sql_filter_where])
        else:
            return queryset
