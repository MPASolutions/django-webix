Admin Site
==========

Example
-------

If you need to override base site class create the files (e.g. <project_name>/dwadmin.py) a
Here an example:

.. code-block:: python

    import datetime
    from django.apps import apps
    from django.conf import settings
    from django.utils.functional import LazyObject
    from django.utils.module_loading import import_string

    class CustomSiteAdminWebixSite(LazyObject):
        def _setup(self):
            AdminWebixSiteClass = import_string(apps.get_app_config('dwadmin').default_site)

            AdminWebixSiteClass.site_url = '/'

            # texts
            AdminWebixSiteClass.site_title = gettext_lazy('Django webix site admin')
            AdminWebixSiteClass.site_header = gettext_lazy('Django webix administration')
            AdminWebixSiteClass.index_title = gettext_lazy('Site administration')

            # form style
            AdminWebixSiteClass.login_form = None
            AdminWebixSiteClass.label_width = None

            # template style
            AdminWebixSiteClass.webix_container_id = 'content_right'
            AdminWebixSiteClass.webix_menu_type = 'menu'  # ['menu', 'sidebar']
            AdminWebixSiteClass.webix_menu_width = 180

            # templates
            AdminWebixSiteClass.index_template = None
            AdminWebixSiteClass.login_template = None
            AdminWebixSiteClass.logout_template = None
            AdminWebixSiteClass.dashboard_template = 'dwadmin/dashboard.js'
            AdminWebixSiteClass.password_change_template = None
            AdminWebixSiteClass.password_change_done_template = None

            # for webgis support
            AdminWebixSiteClass.webgis_template = 'webgis_leaflet/init.js'

            # context for index
            def extra_index_context(self, request):
                if request.session.get('year',None) == None:
                    request.session['year'] = datetime.datetime.today().year
                return {
                    'DEBUG': settings.DEBUG,
                    'years': list(range(2020, datetime.datetime.today().year + 1)),
                }
            AdminWebixSiteClass.extra_index_context = extra_index_context

            # context for each view
            def each_context(self, request):
                return super().each_context(request)
            AdminWebixSiteClass.each_context = each_context

            # dashboard view
            def dashboard(self, request, extra_context=None):
                return super().dashboard(request, extra_context)
            AdminWebixSiteClass.dashboard = dashboard

            self._wrapped = AdminWebixSiteClass()

    custom_site = CustomSiteAdminWebixSite()


Site texts
----------
There are some options for customizate text header into django_webix_admin.

.. code-block:: python

    site_title
    site_header
    index_title

Site templates
--------------
It's possibile to change all main templates.

.. code-block:: python

    index_template
    login_template
    logout_template
    dashboard_template
    password_change_template
    password_change_done_template

Form style
----------
With some variables is possibile to fit better label and field into forms.

.. code-block:: python

    login_form
    label_width

Template style
--------------
There is possibility to customize many and main webix ID key.

.. code-block:: python

    webix_container_id = 'content_right'
    webix_menu_type = 'menu'  # ['menu', 'sidebar']
    webix_menu_width = 180

WebGIS support
--------------
Django webix admin supports gis based on leaflet.
It's posibile to find an example into package templates.

.. code-block:: python

    webgis_template

Context
-------
It's possibile to customizate context for each view and specially for index page.

.. code-block:: python

    def extra_index_context(self, request):
    def each_context(self, request):

Dashboard
---------
You can override main dashboard (not work only on his context).

.. code-block:: python

    def dashboard(self, request, extra_context=None):

