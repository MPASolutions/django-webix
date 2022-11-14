from django.conf import settings
from django.apps import apps

from django_webix.contrib.filter.utils.config import model_is_enabled, get_enable_field


def get_all_fields_from_json(json):
    result = []
    rules = json.get('rules', [])
    for rule in rules:
        if rule.get('id', None) is not None:
            result.append(rule.get('id', None))
        elif rule.get('rules', None) is not None:
            result.extend(get_all_fields_from_json(rule))

    return result


def check_config():
    for k, item in settings.DJANGO_WEBIX_FILTER["models"].items():
        if not isinstance(k, str):
            return (False, 'A key is malformed, is not a string')
        model_name = k.split('.')
        if len(model_name) != 2:
            return (False, 'A key is malformed, it must be composed like app_label.model_name, was found: ' + k)
        model_class = None
        try:
            model_class = apps.get_model(app_label=model_name[0], model_name=model_name[1])
        except:
            return (False, 'A model was not found, model name : ' + k)
        if model_class is None:
            return (False, 'A model was not found, model name : ' + k)
        # ora sono sicuro che il modello c'è
        fields = item.get('fields', None)
        exclude = item.get('exclude', None)
        if fields is not None and exclude is not None:
            return (False, 'A model has defined both exclude and fields, only one must be declared, model name : ' + k)
        model_fields = [x.name for x in model_class._meta.get_fields()]
        if fields is not None:
            missings = [x for x in fields if x not in model_fields]
            if len(missings) > 0:
                return (False, 'A model use fields that do not exists, model name : ' + k + 'fields: ' + str(missings))
        if exclude is not None:
            missings = [x for x in exclude if x not in model_fields]
            if len(missings) > 0:
                return (False, 'A model use fields that do not exists, model name : ' + k + 'fields: ' + str(missings))
    return (True, '')


def check_filter(json):
    if json is None:
        return False
    # here must be the result given by get_JSON_for_JQB
    rules = json.get('rules', None)
    fks = json.get('fks', None)
    if rules is not None and fks is not None:
        fields = get_all_fields_from_json(rules)
        for index, fk in fks.items():
            if fk.get('hops', None) is not None:
                for hop in fk.get('hops', None):
                    fields.append(hop)
        for field in fields:
            names = field.split('.')
            try:
                model_class = apps.get_model(app_label=names[0], model_name=names[1])
                if not model_is_enabled(model_class):
                    return False
                if model_class._meta.get_field(names[2]) not in get_enable_field(model_class):
                    return False
            except:
                return False
    return True
