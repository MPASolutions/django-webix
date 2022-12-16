
from django import template
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist

register = template.Library()


@register.simple_tag(takes_context=True)
def field_type(context, model, field_name):
    """ Returns model field type """

    app_label, model = model.split(".")
    model_class = apps.get_model(app_label=app_label, model_name=model)
    field = None
    for name in field_name.split('__'):
        try:
            field = model_class._meta.get_field(name)
        except FieldDoesNotExist:
            # name is probably a lookup or transform such as __contains
            break
        if hasattr(field, 'related_model'):
            # field is a relation
            model_class = field.related_model
        else:
            # field is not a relation, any name that follows is probably a lookup or transform
            break
    return field.__class__.__name__ if field else None
