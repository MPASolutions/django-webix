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
                qset_to_applicate = Q(**{data_qset.get('path'): data_qset.get('val')})
            if j == 0:
                qset = qset_to_applicate
            else:
                if operator == 'AND':
                    qset = qset & qset_to_applicate
                elif operator == 'OR':
                    qset = qset | qset_to_applicate
        if negate == True:
            qset = ~Q(qset)
    elif 'path' in data and 'val' in data:
        qset = Q(**{data.get('path'): data.get('val')})
    else:
        qset = Q()
    return qset
