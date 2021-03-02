# -*- coding: utf-8 -*-

def register(*models, site=None):
    """
    Register the given model(s) classes and wrapped ModelWebixAdmin class with
    admin site:
    @register(Author)
    class AuthorAdmin(admin.ModelAdmin):
        pass
    The `site` kwarg is an admin site to use instead of the default admin site.

    :param models:
    :param site:
    :return:
    """

    from django_webix.admin_webix import ModelWebixAdmin
    from django_webix.admin_webix.sites import site as default_site, AdminWebixSite

    def _model_admin_wrapper(admin_class):
        if not models:
            raise ValueError('At least one model must be passed to register.')

        admin_site = site or default_site

        if not isinstance(admin_site, AdminWebixSite):
            raise ValueError('site must subclass AdminSite')

        if not issubclass(admin_class, ModelWebixAdmin):
            raise ValueError('Wrapped class must subclass ModelAdmin.')

        admin_site.register(models, admin_class=admin_class)

        return admin_class

    return _model_admin_wrapper
