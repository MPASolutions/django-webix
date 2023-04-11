from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey

from django_webix.contrib.filter.utils.operators import operators_override, counter_operator, matches


def _get_config_new(model_class):
    fields = []
    prefix_id = '{app_label}.{model_name}.'.format(
        app_label=model_class._meta.app_label,
        model_name=model_class._meta.model_name
    )
    # Iterate through model fields excluding relations and adds it to model configuration dict
    for field in get_enable_field(model_class):
        # da escludere questi campi
        if issubclass(type(field), GenericForeignKey):
            continue
        if issubclass(type(field), models.ForeignKey):
            model = field.remote_field.get_related_field().model
            model_name = "{app_label}.{model_name}".format(
                app_label=model._meta.app_label,
                model_name=model._meta.model_name
            )
            fields_to_insert = {
                "id": prefix_id + field.name,
                "label": field.verbose_name,
                "type": field.get_internal_type(),
                "operators": list(field.get_lookups().keys()),
                "follow": True,
                "follow_model": model_name
            }
        elif issubclass(type(field), ForeignObjectRel):
            model = field.related_model
            model_name = "{app_label}.{model_name}".format(
                app_label=model._meta.app_label,
                model_name=model._meta.model_name
            )
            fields_to_insert = {
                "id": prefix_id + field.remote_field.related_query_name(),
                "label": model._meta.verbose_name_plural,
                "type": field.get_internal_type(),
                "operators": list(field.remote_field.get_lookups().keys()),
                "follow": True,
                "follow_model": model_name
            }
        elif issubclass(type(field), models.ManyToManyField):
            model = field.remote_field.get_related_field().model
            model_name = "{app_label}.{model_name}".format(
                app_label=model._meta.app_label,
                model_name=model._meta.model_name,
                model_prefix=model._meta.verbose_name
            )
            fields_to_insert = {
                "id": prefix_id + field.name,
                "label": field.verbose_name,
                "type": field.get_internal_type(),
                "operators": list(field.get_lookups().keys()),
                "follow": True,
                "follow_model": model_name
            }
        # generic models
        elif issubclass(type(field), GenericRelation):
            model = field.related_model
            model_name = "{app_label}.{model_name}".format(
                app_label=model._meta.app_label,
                model_name=model._meta.model_name,
                model_prefix=model._meta.verbose_name
            )
            fields_to_insert = {
                "id": prefix_id + field.name,
                "label": field.verbose_name,
                "type": field.get_internal_type(),
                "operators": list(field.get_lookups().keys()),
                "follow": True,
                "follow_model": model_name
            }
        else:
            fields_to_insert = {
                "id": prefix_id + field.name,
                "label": field.verbose_name,
                "type": field.get_internal_type(),
                "operators": list(field.get_lookups().keys()),
            }
            if (
                hasattr(field, "base_field") and
                hasattr(field.base_field, 'choices') and
                field.base_field.choices is not None and
                len(field.base_field.choices) > 0
            ):

                fields_to_insert.update({
                    # 'input': 'select',
                    "operators": ["exact", "isnull"],
                    "values": [{x[0]: x[1]} for x in field.base_field.choices]
                })

                if not isinstance(field, ArrayField):
                    fields_to_insert.update({
                        'input': 'select'
                    })

            if (
                hasattr(field, 'choices') and
                field.choices is not None and
                len(field.choices) > 0
            ):
                fields_to_insert.update({
                    'input': 'select',
                    "operators": ["exact", "isnull"],
                    "values": [{x[0]: x[1]} for x in field.choices]
                })

        for operator in fields_to_insert['operators']:
            if counter_operator.get(operator, None) is not None:
                fields_to_insert['operators'].append(counter_operator.get(operator, None))

        ovveride = matches.get(type(field), None)
        if ovveride is not None:
            if ovveride.get('operators', None) is not None:
                fields_to_insert['operators'] = ovveride.get('operators', None)
            if ovveride.get('input') is not None:
                fields_to_insert['input'] = ovveride.get('input', None)
            if ovveride.get('values') is not None:
                fields_to_insert['values'] = ovveride.get('values', None)
            if ovveride.get('webix_type') is not None:
                fields_to_insert['webix_type'] = ovveride.get('webix_type', None)
            if ovveride.get('plugin_webix') is not None:
                fields_to_insert['plugin_webix'] = ovveride.get('plugin_webix', None)

        fields_to_insert.update({
            'value_separator': ';',
        })

        fields.append(fields_to_insert)

    # operators = list(set([operator for field in fields for operator in field["operators"]]))
    op_final = []

    for k, v in operators_override.items():
        item = {
            'name': k,
            'label': v.get('label', k),
            'nb_inputs': v.get('nb_inputs', 1),
            'multiple': v.get('multiple', False),
            'values': v.get('values', None),
            'pick_geometry': v.get('pick_geometry', False),
        }
        op_final.append(item)

    return {
        "model": "{app_label}.{model_name}".format(
            app_label=model_class._meta.app_label,
            model_name=model_class._meta.model_name
        ),
        "label": model_class._meta.verbose_name,
        "fields": fields,
        "operators": op_final
    }


def get_enabled_model(initial=False):
    result = []
    for key, value in settings.DJANGO_WEBIX_FILTER["models"].items():
        if initial is True and isinstance(value, dict) and 'initial' in value and value['initial'] is False:
            continue  # Non enabled to initial filter
        app_label, model_name = key.split(".")
        try:
            model = apps.get_model(app_label, model_name)
        except:
            pass
        else:
            result.append(model)
    return result


def model_is_enabled(model, initial=False):
    if model in get_enabled_model(initial):
        return True
    return False


def get_enable_field(model):
    if model is None:
        return []
    if not model_is_enabled(model):
        return []

    field_def = model._meta.get_fields()
    filter_sett = settings.DJANGO_WEBIX_FILTER["models"]
    modello = filter_sett.get("{}.{}".format(model._meta.app_label, model._meta.model_name), None)
    campi_inclusi = modello.get('fields', None)
    campi_esclusi = modello.get('exclude', None)
    result = []
    if campi_inclusi is not None and campi_esclusi is not None:
        pre_result = field_def
    elif campi_inclusi is not None:
        pre_result = [x for x in field_def if x.name in campi_inclusi]
    elif campi_esclusi is not None:
        pre_result = [x for x in field_def if x.name not in campi_esclusi]
    else:
        pre_result = field_def

    # check delle FK
    for field in pre_result:
        next_model = None
        if issubclass(type(field), models.ForeignKey):
            next_model = field.remote_field.get_related_field().model
        elif issubclass(type(field), ForeignObjectRel):
            next_model = field.related_model
        elif issubclass(type(field), models.ManyToManyField):
            next_model = field.remote_field.get_related_field().model
        elif issubclass(type(field), models.ManyToManyField):
            next_model = field.related_model

        if next_model is not None:
            if model_is_enabled(next_model):
                result.append(field)
        else:
            result.append(field)
    return result


def get_limit_suggest():
    if 'AUTOCOMPLETE_LIMITS' in settings.DJANGO_WEBIX_FILTER:
        return settings.DJANGO_WEBIX_FILTER['AUTOCOMPLETE_LIMITS']
    # dafualt
    return 30
