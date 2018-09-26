.. _Webix: https://webix.com

Django Webix
============

Use the Webix_ JavaScript UI library with Django

Documentation
-------------

The full documentation is at https://django-webix.readthedocs.io.

Quickstart
----------

Install Django Webix:

.. code-block:: bash

    $ pip install django-webix

Add ``django-webix`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_webix',
        # ...
    ]

Add ``django-webix`` URLconf to your project ``urls.py`` file

.. code-block:: python

    from django.conf.urls import url, include

    urlpatterns = [
        # ...
        url(r'^django-webix/', include('django_webix.urls')),
        # ...
    ]

Include ``webix static files`` folder in your django staticfiles folder as ``webix``


Running Tests
-------------

Does the code actually work?

.. code-block:: bash

    $ source <YOURVIRTUALENV>/bin/activate
    $ (myenv) $ pip install tox
    $ (myenv) $ tox
