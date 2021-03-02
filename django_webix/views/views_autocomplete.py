# -*- coding: utf-8 -*-

import json
import operator
from functools import reduce

from django.apps import apps
from django.conf import settings
from django.contrib.admin.utils import prepare_lookup_value
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, connection
from django.db.models import Q, QuerySet
from django.db.models.constants import LOOKUP_SEP
from django.http import HttpResponse
from django.utils.encoding import smart_text
from django.views import View
from django.views.decorators.cache import never_cache

AUTOCOMPLETE_SEARCH_FIELDS = getattr(settings, "WEBIX_AUTOCOMPLETE_SEARCH_FIELDS", {})


def get_label(f):
    return f.related_label() if getattr(f, "related_label", None) else smart_text(f)


def ajax_response(data):
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/javascript')


class RelatedLookup(View):
    "Related Lookup"

    def check_user_permission(self):
        """ CUSTOM """

        if not (self.request.user.is_active and self.request.user.is_authenticated):
            raise PermissionDenied

    def get_model(self):
        try:
            self.model = apps.get_model(self.GET['app_label'], self.GET['model_name'])
        except LookupError:
            self.model = None
        return self.model

    def get_filtered_queryset(self, qs):
        """ CUSTOM """

        query_string = self.GET.get('query_string', None)
        qset = Q()
        if query_string:
            for j, item2 in enumerate(query_string.split("|")):  # OR
                filters = {}
                for item in item2.split(":"):  # AND
                    k, v = item.split("=")
                    VALUE = smart_text(v)
                    if VALUE == 'TRUE':
                        VALUE = True
                    elif VALUE == 'FALSE':
                        VALUE = False
                    elif 'None' in VALUE:
                        VALUE = False
                    if k != "_to_field":
                        filters[smart_text(k)] = prepare_lookup_value(smart_text(k), VALUE)
                qset |= Q(**filters)
        try:
            qs = qs.filter(qset)
        except:
            qs = qs.none()
        return qs

    def get_queryset(self):
        qs = self.model._default_manager.get_queryset()
        # model_admin = self.get_model_admin()
        # if model_admin is not None:
        #     qs = model_admin.get_queryset(self.request)
        qs = self.get_filtered_queryset(qs)
        return qs


class AutocompleteWebixLookup(RelatedLookup):
    "AutocompleteLookup"

    def request_is_valid(self):
        return 'filter[value]' in self.GET and 'app_label' in self.GET and 'model_name' in self.GET

    def get_searched_queryset(self, qs):
        """ CUSTOM """

        model = self.model
        term = self.GET["filter[value]"]  # ho cambiato da "term" a "filter[value]"
        try:
            term = model.autocomplete_term_adjust(term)
        except AttributeError:
            pass

        try:
            search_fields = model.autocomplete_search_fields()
        except AttributeError:
            try:
                search_fields = AUTOCOMPLETE_SEARCH_FIELDS[model._meta.app_label][model._meta.module_name]
            except KeyError:
                search_fields = ()

        if search_fields:
            for word in term.split():
                search = [models.Q(**{smart_text(item): smart_text(word)}) for item in search_fields]
                search_qs = QuerySet(model)
                search_qs.query.select_related = qs.query.select_related
                search_qs = search_qs.filter(reduce(operator.or_, search))
                qs &= search_qs
        else:
            qs = model.objects.none()
        return qs

    def get_final_ordering(self, model, previous_lookup_parts=None):
        """
        This recursive function returns the final lookups
        for the default ordering of a model.

        Considering the models below, `get_final_ordering(Book)` will return
        `['-type__name', 'name']` instead of the simple `['-type', 'name']`
        one would get using `Book._meta.ordering`.

            class BookType(Model):
                name = CharField(max_length=50)

                class Meta:
                    ordering = ['name']

            class Book(Model):
                name = CharField(max_length=50)
                type = ForeignKey(BookType)

                class Meta:
                    ordering = ['-type', 'name']
        """
        ordering = []
        for lookup in model._meta.ordering:
            opts = model._meta
            for part in lookup.lstrip('-').split(LOOKUP_SEP):
                field = opts.get_field(part)
                if field.is_relation:
                    opts = field.rel.to._meta if hasattr(field, 'rel') else field.related_model._meta
            if previous_lookup_parts is not None:
                lookup = previous_lookup_parts + LOOKUP_SEP + lookup
            if field.is_relation:
                ordering.extend(self.get_final_ordering(opts.model, lookup))
            else:
                ordering.append(lookup)
        return ordering

    def get_queryset(self):
        qs = super(AutocompleteWebixLookup, self).get_queryset()
        qs = self.get_filtered_queryset(qs)
        qs = self.get_searched_queryset(qs)

        if connection.vendor == 'postgresql':
            ordering = self.get_final_ordering(self.model)
            distinct_columns = [o.lstrip('-') for o in ordering]
            pk_name = self.model._meta.pk.name
            if pk_name not in distinct_columns:
                distinct_columns.append(pk_name)
            return qs.order_by(*ordering).distinct(*distinct_columns)

        return qs.distinct()

    def get_data(self):
        to_field = self.GET.get("to_field", 'pk')
        if self.GET.get("nolimit", None):
            _AUTOCOMPLETE_LIMIT = 1000
        else:
            _AUTOCOMPLETE_LIMIT = 50
        return [{
            "id": '%s' % getattr(f, to_field),
            "value": get_label(f)
        } for f in self.get_queryset()[:_AUTOCOMPLETE_LIMIT]]

    @never_cache
    def get(self, request, *args, **kwargs):
        self.check_user_permission()
        self.GET = self.request.GET

        if self.request_is_valid():
            self.get_model()
            if self.model is not None:
                data = self.get_data()
                if data:
                    return ajax_response(data)

        # overcomplicated label translation
        data = []
        return ajax_response(data)
