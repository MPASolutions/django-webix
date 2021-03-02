# -*- coding: utf-8 -*-

import types

from django.contrib.admin.utils import NestedObjects
from django.contrib.gis.db import models
from django.utils.encoding import force_text
from django.utils.text import capfirst

geo_field_classes = {
    "POINT": models.PointField,
    "MULTIPOINT": models.MultiPointField,
    "LINESTRING": models.LineStringField,
    "MULTILINESTRING": models.MultiLineStringField,
    "POLYGON": models.PolygonField,
    "MULTIPOLYGON": models.MultiPolygonField,
    "GEOMETRYCOLLECTION": models.GeometryCollectionField,
    "GEOMETRY": models.GeometryField
}


def get_model_geo_field_names(model):
    geo_field_names = []
    for field in model._meta.fields:
        if type(field) in geo_field_classes.values():
            geo_field_names.append(field.name)
    return geo_field_names


def walk_items(item_list):
    item_iterator = iter(item_list)
    try:
        item = next(item_iterator)
        while True:
            try:
                next_item = next(item_iterator)
            except StopIteration:
                yield item, None
                break
            if isinstance(next_item, (list, tuple, types.GeneratorType)):
                try:
                    iter(next_item)
                except TypeError:  # pragma: no cover
                    pass
                else:
                    yield item, next_item
                    item = next(item_iterator)
                    continue  # pragma: no cover
            yield item, None
            item = next_item
    except StopIteration:
        pass


def tree_formatter(item_list):
    output = []
    for item, children in walk_items(item_list):
        _data = {"value": '{}: {}'.format(capfirst(item._meta.verbose_name), force_text(item))}
        _sub_data = None
        if children:
            _data.update({"data": tree_formatter(children), "open": True})
        output.append(_data)
    return output


class NestedObjectsWithLimit(NestedObjects):
    exclude_models = None
    only_models = None

    def __init__(self, *args, **kwargs):
        self.exclude_models = kwargs.pop('exclude_models', None)
        self.only_models = kwargs.pop('only_models', None)
        if self.exclude_models is not None and self.only_models is not None:
            raise Exception('Set only one of exclude_models or only_models parameter')
        super().__init__(*args, **kwargs)

    def add_edge(self, source, target):
        if self.only_models is None or (source is None or source._meta.model in self.only_models):
            if self.only_models is None or (target is not None and target._meta.model in self.only_models):
                super(NestedObjectsWithLimit, self).add_edge(source, target)
        elif self.exclude_models is None or (source is None or source._meta.model not in self.exclude_models):
            if self.exclude_models is None or (target is not None and target._meta.model not in self.only_models):
                super(NestedObjectsWithLimit, self).add_edge(source, target)
