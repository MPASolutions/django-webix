# INFO: is not possibile to invalidate cache and set again in ready() method
# because is call from different threads and services

from django.conf import settings

if getattr(settings, "WEBIX_EXTRA_FIELDS_ENABLE_CACHE", False):
    from django.db.models.signals import post_delete, post_save
    from django.dispatch import receiver
    from django_webix.contrib.extra_fields.models import ModelField, ModelFieldChoice
    from django_webix.contrib.extra_fields.utils_cache import set_cache_extra_fields

    @receiver(post_save, sender=ModelField)
    def handle_ModelField_post_save(sender, instance, created, **kwargs):
        set_cache_extra_fields(force=True)

    @receiver(post_delete, sender=ModelField)
    def handle_ModelField_post_delete(sender, instance, **kwargs):
        set_cache_extra_fields(force=True)

    @receiver(post_save, sender=ModelFieldChoice)
    def handle_ModelFieldChoice_post_save(sender, instance, created, **kwargs):
        set_cache_extra_fields(force=True)

    @receiver(post_delete, sender=ModelFieldChoice)
    def handle_ModelFieldChoice_post_delete(sender, instance, **kwargs):
        set_cache_extra_fields(force=True)
