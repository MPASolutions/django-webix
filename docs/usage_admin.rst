Admin
=====

.. image:: static/django_webix_admin_list.png
  :alt: Django-Webix admin list example

.. image:: static/django_webix_admin_form.png
  :alt: Django-Webix admin form example

Configure
---------

Settings
~~~~~~~~

Description

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_webix',
        # ...
    ]


Usage
-----

Admin Webix
~~~~~~~~~~~

Create the forms (e.g. <app_name>/admin_webix.py)

.. code-block:: python

    from anagrafica.models import Conferente
    from appezzamenti.models import Appezzamento, UnitaVitata
    from django_webix import admin_webix as admin


    @admin.register(Conferente)
    class ConferenteAdmin(admin.ModelWebixAdmin):
        list_display = ['ragione_sociale', 'partita_iva', 'email']
        enable_json_loading = True


    @admin.register(Appezzamento)
    class AppezzamentoAdmin(admin.ModelWebixAdmin):
        list_display = ['conferente__ragione_sociale', 'codice', 'denominazione']
        enable_json_loading = True


    @admin.register(UnitaVitata)
    class UnitaVitataAdmin(admin.ModelWebixAdmin):
        list_display = ['conferente__ragione_sociale', 'comune_amministrativo__comune', 'particella_catastale',
                        'foglio_catastale', 'codice']
        enable_json_loading = True


Urls
~~~~

Register the views url (e.g. <project_name>/urls.py)

.. code-block:: python

    from django.conf.urls import url

    from <app_name>.views import HomeView, MyModelListView, MyModelCreateView, MyModelUpdateView, MyModelDeleteView

    urlpatterns = [
      path('admin_webix/', admin_webix.site.urls), # TEST
    ]

