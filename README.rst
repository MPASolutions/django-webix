.. _Webix: https://webix.com

Django Webix
============


.. image:: https://badge.fury.io/py/django-webix.svg
    :target: https://badge.fury.io/py/django-webix
    :alt: Version

.. image:: https://travis-ci.org/MPASolutions/django-webix.svg?branch=master
    :target: https://travis-ci.org/MPASolutions/django-webix
    :alt: Build

.. image:: https://readthedocs.org/projects/django-webix/badge/?version=latest
    :target: http://django-webix.readthedocs.org/en/latest/?badge=latest

.. image:: https://codecov.io/gh/MPASolutions/django-webix/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/MPASolutions/django-webix
    :alt: Codecov

.. image:: https://img.shields.io/github/issues/MPASolutions/django-webix.svg
    :target: https://github.com/MPASolutions/django-webix/issues
    :alt: Issues

.. image:: https://img.shields.io/pypi/pyversions/django-webix.svg
    :target: https://img.shields.io/pypi/pyversions/django-webix.svg
    :alt: Py versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://raw.githubusercontent.com/MPASolutions/django-webix/master/LICENSE
    :alt: License

Use the Webix_ JavaScript UI library with Django

Documentation
-------------

The full documentation is at https://django-webix.readthedocs.io.


Quickstart
----------

Create a new virtualenv:

.. code-block:: bash

    $ python -m venv django-webix
    $ source django-webix/bin/activate


Install Django Webix:

.. code-block:: bash

    $ pip install django-webix

Extra packages for Django Webix:

.. code-block:: bash

    $ pip install django-webix-sender
    $ pip install django-dal
    $ pip install django-filtersmerger
    $ pip install django-webix-filter

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

Add internationalization to `TEMPLATES`

.. code-block:: python

    TEMPLATES = [
        {
            # ...
            'OPTIONS': {
                'context_processors': [
                    # ...
                    'django.template.context_processors.i18n',
                ],
            },
        },
    ]

Include ``webix static files`` folder in your django staticfiles folder as ``webix`` and add static configuration

.. code-block:: python

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'staticfiles'),
    )
    STATIC_URL = '/static/'


Running Tests
-------------

Does the code actually work?

.. code-block:: bash

    $ source <YOURVIRTUALENV>/bin/activate
    $ (myenv) $ pip install tox
    $ (myenv) $ tox


Sponsors
--------

.. image:: https://mpasolutions.it/img/logo.png
    :target: https://mpasolutions.it
    :alt: MPA Solutions

.. image:: https://www.enogis.it/wp-content/uploads/2020/09/enogis_flat_logo.png
    :target: https://enogis.it
    :alt: Enogis


Contributors
------------

Here is a list of Django-Webix's contributors.

.. image:: https://contributors-img.web.app/image?repo=MPASolutions/django-webix
    :target: https://github.com/MPASolutions/django-webix/graphs/contributors
    :alt: Contributors
