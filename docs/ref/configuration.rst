Configuration
==============

Installation
------------

``django-webix`` is available on `PyPI <https://pypi.python.org/pypi/django-webix/>`_:

.. code-block:: bash

    $ pip install django-webix


Setup
-----

INSTALLED_APPS
~~~~~~~~~~~~~~

Add ``django_webix`` to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_webix',
        # ...
    ]

URLs
~~~~

Add ``django-webix`` URLconf to your project ``urls.py`` file:

.. code-block:: python

    from django.urls import path, include

    urlpatterns = [
        # ...
        path('django-webix/', include('django_webix.urls')),
        # ...
    ]

Templates
~~~~~~~~~

Add internationalization to ``TEMPLATES``:

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

Static Files
~~~~~~~~~~~~

Include ``webix static files`` folder in your Django staticfiles configuration:

.. code-block:: python

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'staticfiles'),
    )
    STATIC_URL = '/static/'


Configuration Variables
-----------------------

Required Settings
~~~~~~~~~~~~~~~~~

These settings **must** be defined in your ``settings.py``:

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Setting
     - Example
     - Description
   * - ``WEBIX_LICENSE``
     - ``'PRO'``
     - Webix license type. Set to ``'PRO'`` for Webix PRO features (required for
       ``ModelMultipleChoiceField`` / ``multicombo`` widget) or ``'FREE'`` for the open-source version.
   * - ``WEBIX_VERSION``
     - ``'9.4.0'``
     - The version of the Webix JS library being used. This affects date picker behavior and
       other version-specific rendering.
   * - ``WEBIX_CONTAINER_ID``
     - ``'content_right'``
     - The DOM element ID where Webix views are rendered. This must match the ``id`` of the
       container element in your base HTML template.

Optional Settings
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Setting
     - Default
     - Description
   * - ``WEBIX_OVERLAY_CONTAINER_ID``
     - Same as ``WEBIX_CONTAINER_ID``
     - The DOM element ID used for overlay (loading) indicators. Defaults to the same value
       as ``WEBIX_CONTAINER_ID``.
   * - ``WEBIX_FONTAWESOME_CSS_URL``
     - ``'fontawesome/css/all.min.css'``
     - Path to the Font Awesome CSS file (relative to ``STATIC_URL``).
   * - ``WEBIX_FONTAWESOME_VERSION``
     - ``'5.13.1'``
     - Font Awesome version string.
   * - ``WEBIX_HISTORY_ENABLE``
     - ``False``
     - Enable browser history integration for Webix SPA navigation. When ``True``, URL changes
       are pushed to the browser history, enabling back/forward navigation.
   * - ``DEBUG_WEBIX``
     - ``False``
     - Enable debug mode for django-webix. Shows additional logging and debug information.
   * - ``WEBIX_MULTIPLE_DELETE_CONFIRMATION``
     - ``True``
     - Whether to show a confirmation dialog before bulk delete actions. Set to ``False`` to
       skip confirmation.


Complete Minimal ``settings.py`` Example
----------------------------------------

.. code-block:: python

    import os

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_webix',
        # your apps...
    ]

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'django.template.context_processors.i18n',
                ],
            },
        },
    ]

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'staticfiles'),
    )
    STATIC_URL = '/static/'

    # django-webix configuration
    WEBIX_LICENSE = 'PRO'
    WEBIX_VERSION = '9.4.0'
    WEBIX_CONTAINER_ID = 'content_right'
    WEBIX_FONTAWESOME_CSS_URL = 'fontawesome/css/all.min.css'
    WEBIX_FONTAWESOME_VERSION = '5.13.1'
    WEBIX_HISTORY_ENABLE = True
