# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Q


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
