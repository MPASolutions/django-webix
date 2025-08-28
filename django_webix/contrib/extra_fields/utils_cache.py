from django.core.cache import cache


def set_cache_extra_fields(force=False):
    if cache.get("django_webix_extra_fields", None) is None or force is True:
        from django_webix.contrib.extra_fields.models import ModelField

        extra_fields = {}
        for content_type_id in ModelField.objects.values_list("content_type_id", flat=True).distinct():
            extra_fields.update({content_type_id: []})
            for field in ModelField.objects.filter(content_type_id=content_type_id):
                choices = list(field.modelfieldchoice_set.values("key", "value"))
                extra_fields[content_type_id].append(
                    {
                        "pk": field.pk,
                        "field_type": field.field_type,
                        "field_name": field.field_name,
                        "related_to": field.related_to,
                        "label": field.label,
                        "locked": field.locked,
                        "has_choices": len(choices) > 0,
                        "choices": choices,
                    }
                )

        cache.set("django_webix_extra_fields", extra_fields)
