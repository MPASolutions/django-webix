Admin Site
=====

Site class customization
~~~~~~~~

If you need to override base site class create the files (e.g. <project_name>/admin_webix.py) a
Here an example:

.. code-block:: python

    import datetime
    from django.apps import apps
    from django.conf import settings
    from django.utils.functional import LazyObject
    from django.utils.module_loading import import_string

    class CustomSiteAdminWebixSite(LazyObject):
        def _setup(self):
            AdminWebixSiteClass = import_string(apps.get_app_config('admin_webix').default_site)

            # parameters
            AdminWebixSiteClass.site_title = gettext_lazy('Django webix site admin')
            AdminWebixSiteClass.site_header = gettext_lazy('Django webix administration')
            AdminWebixSiteClass.index_title = gettext_lazy('Site administration')
            AdminWebixSiteClass.site_url = '/'
            AdminWebixSiteClass.login_form = None
            AdminWebixSiteClass.label_width = None
            AdminWebixSiteClass.webix_container_id = 'content_right'
            AdminWebixSiteClass.webix_menu_type = 'menu'  # ['menu', 'sidebar']
            AdminWebixSiteClass.webix_menu_width = 180
            AdminWebixSiteClass.index_template = None
            AdminWebixSiteClass.login_template = None
            AdminWebixSiteClass.logout_template = None
            AdminWebixSiteClass.dashboard_template = 'admin_webix/dashboard.js'
            AdminWebixSiteClass.password_change_template = None
            AdminWebixSiteClass.password_change_done_template = None

            # for webgis support
            AdminWebixSiteClass.webgis_template = 'webgis_leaflet/init.js'

            # functions
            def extra_index_context(self, request):
                if request.session.get('year',None) == None:
                    request.session['year'] = datetime.datetime.today().year
                return {
                    'DEBUG': settings.DEBUG,
                    'years': list(range(2020, datetime.datetime.today().year + 1)),
                }
            AdminWebixSiteClass.extra_index_context = extra_index_context

            def each_context(self, request):
                return super().each_context(request)
            AdminWebixSiteClass.each_context = each_context

            def dashboard(self, request, extra_context=None):
                return super().dashboard(request, extra_context)
            AdminWebixSiteClass.dashboard = dashboard

            def extra_index_context(self, request):
                return {}
            AdminWebixSiteClass.extra_index_context = extra_index_context

            self._wrapped = AdminWebixSiteClass()

    custom_site = CustomSiteAdminWebixSite()

