# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import types

from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.text import capfirst


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
        if hasattr(item, 'get_url_update') and item.get_url_update is not None:
            _data.update({'url': reverse(item.get_url_update, kwargs={"pk": item.pk})})
        if children:
            _data.update({"data": tree_formatter(children), "open": True})
        output.append(_data)
    return output
