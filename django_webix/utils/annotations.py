from django.apps import apps
from django.db.models import Case, When, Value, CharField


def annotate_display(model, field_name):
    """
    map field choices with display name, usefull in queryset annotate
    NB: con lazy string importante usare str(v)
    :param model: the model class which refer the field
    :param field_name: model field name
    :return: django case expressions
    """

    return Case(
        *[When(**{field_name: k}, then=Value(str(v))) for k, v in model._meta.get_field(field_name).choices],
        default=Value(''),
        output_field=CharField()
    )


def annotate_contenttype_verbose(model, field_name):
    """
    map content type model with verbose name, usefull in queryset annotate
    :param model: the model class which refer the field
    :param field_name: model field name
    :return: django case expressions
    """

    return Case(
        *[When(
            **{field_name: ct_id},
            then=Value(str(apps.get_model(ct_app_label, ct_model)._meta.verbose_name))
        ) for ct_id, ct_app_label, ct_model in model.objects.values_list(
            f'{field_name}_id',
            f'{field_name}__app_label',
            f'{field_name}__model'
        ).order_by().distinct()],
        default=Value(''),
        output_field=CharField()
    )
