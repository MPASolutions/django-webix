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

    from django.urls import path

    from <somewhere> import dwadmin

    urlpatterns = [
      path('admin_webix/', dwadmin.site.urls), # or another path :-)
    ]
