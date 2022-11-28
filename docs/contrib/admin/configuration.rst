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
        'django_webix.contrib.admin',
        # ...
    ]


Urls
~~~~

Register the views url (e.g. <project_name>/urls.py)

.. code-block:: python

    from django.conf.urls import url

    from <somewhere> import admin_webix

    urlpatterns = [
      path('admin_webix/', admin_webix.site.urls), # or another path :-)
    ]

