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
