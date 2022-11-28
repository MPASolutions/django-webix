from django.db import models
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey


def get_JSON_for_JQB(filtro, model_class):
    index = 0
    rules_result = {}
    rules_dependecy = {}
    if filtro is not None and filtro.get('rules') is not None:
        r = filtro.get('rules')
        index = tree_visit(r, rules_dependecy, index, model_class)
    rules_result = {
        'rules': filtro,
        'fks': rules_dependecy
    }
    return rules_result


def get_JSON_for_DB(filtro):
    result = {}

    if filtro is not None and filtro.get('condition') is not None and filtro.get('rules'):
        result.update({
            'operator': filtro.get('condition', 'AND'),
            'negate': filtro.get('not', True),
        })
        qsets = []
        for rule in filtro.get('rules', []):
            if rule.get('condition') is not None:
                qsets.append(get_JSON_for_DB(rule))
            elif rule.get('id') is not None:
                entry = {
                    'path': rule.get('id', '') + '__' + rule.get('operator', ''),
                    'val': rule.get('value')
                }
                qsets.append(entry)
        result.update({
            'qsets': qsets
        })

    return result


def get_JSON_from_DB(filtro):
    result = {}

    if filtro is not None and filtro.get('operator') is not None and filtro.get('qsets'):
        result.update({
            'condition': filtro.get('operator', 'AND'),
            'not': filtro.get('negate', True),
            'valid': True
        })
        rules = []
        for qset in filtro.get('qsets', []):
            if qset.get('operator') is not None:
                rules.append(get_JSON_from_DB(qset))
            elif qset.get('path') is not None:
                path = qset.get('path').split('__')
                operator = path.pop()
                path = '__'.join(path)
                entry = {
                    'id': path,
                    'field': path,
                    'type': 'string',
                    'operator': operator,
                    'value': qset.get('val', None)
                }
                rules.append(entry)
        result.update({
            'rules': rules
        })

    return result


def tree_visit(rules, d, index, model_class):
    base_name = model_class._meta.app_label + '.' + model_class._meta.model_name + '.'
    for rule in rules:
        if rule.get('condition') is not None:
            index = tree_visit(rule.get('rules', None), d, index, model_class)
        else:
            fields = rule.get('id', '').split('__')
            fields.reverse()
            field_base = fields.pop()
            fields.reverse()
            name_field_base = base_name + field_base
            rule['id'] = name_field_base
            rule['field'] = name_field_base

            filter_extra = {
                'start_field': name_field_base,
                'hops': [],
                'operator': rule['operator'],
                'value': rule['value']
            }

            model_field = list(
                filter(
                    lambda f: f.name == field_base,
                    model_class._meta.get_fields()
                ))
            if len(model_field) > 1:
                raise Exception('Error found a repeating field ?')
            model_field = model_field[0]
            next_model = None
            if issubclass(type(model_field), models.ForeignKey) or \
                issubclass(type(model_field), ForeignObjectRel) or \
                issubclass(type(model_field), models.ManyToManyField) or \
                issubclass(type(model_field), GenericRelation):
                if issubclass(type(model_field), models.ForeignKey):
                    next_model = model_field.remote_field.get_related_field().model
                elif issubclass(type(model_field), ForeignObjectRel):
                    next_model = model_field.related_model
                elif issubclass(type(model_field), models.ManyToManyField):
                    next_model = model_field.remote_field.get_related_field().model
                elif issubclass(type(model_field), GenericRelation):
                    next_model = model_field.related_model

            for field in fields:
                model_field = list(
                    filter(
                        lambda f: f.name == field,
                        next_model._meta.get_fields()
                    ))
                if len(model_field) > 1:
                    raise Exception('Error found a repeating field ?')

                model_field = model_field[0]
                model_name = next_model._meta.app_label + '.' + next_model._meta.model_name + '.'

                if issubclass(type(model_field), models.ForeignKey):
                    next_model = model_field.remote_field.get_related_field().model
                elif issubclass(type(model_field), ForeignObjectRel):
                    next_model = model_field.related_model
                elif issubclass(type(model_field), models.ManyToManyField):
                    next_model = model_field.remote_field.get_related_field().model
                elif issubclass(type(model_field), GenericRelation):
                    next_model = model_field.related_model

                filter_extra['hops'].append(model_name + field)

            if len(filter_extra['hops']) > 0:
                d[index] = filter_extra

            index += 1
    return index
