import json

from django.db.models import Q

from django_filtersmerger import RequestFilter
from django_webix.utils.filters import from_dict_to_qset
from django_webix.contrib.filter.models import WebixFilter
from django_webix.contrib.filter.utils.json_converter import get_JSON_for_DB


class DjangoAdvancedOTFWebixFilter(RequestFilter):
    PARAM = 'OTFFILTER'

    def filter_queryset(self, queryset, **kwargs):
        otf_filter = self.get_param(self.PARAM)
        if otf_filter not in [None, '']:
            otf_qset = from_dict_to_qset(get_JSON_for_DB(json.loads(otf_filter)), model=queryset.model)
            queryset = queryset.filter(otf_qset)
        return queryset


class DjangoAdvancedWebixFilter(RequestFilter):

    PARAM = 'ADVANCEDFILTER'

    def filter_queryset(self, queryset, **kwargs):
        # attention leaflet fails to send the list as usually happens in the GET / PORT param of jquery, so a split is needed
        dwf_ids = self.get_param(self.PARAM)
        if dwf_ids not in [None, '']:
            dwf_ids = dwf_ids.split(',')
            qs_django_webix_filter = WebixFilter.objects.filter(id__in=dwf_ids)
            dwf_qset = Q()
            for django_webix_filter in qs_django_webix_filter:
                dwf_qset &= from_dict_to_qset(django_webix_filter.filter, model=queryset.model)
            queryset = queryset.filter(dwf_qset)
        return queryset
