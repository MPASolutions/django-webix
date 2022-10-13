Configuration
==============

Install
-------

``django-webix`` is available on :samp:`https://pypi.python.org/pypi/django-webix/` install it simply with:

.. code-block:: bash

    $ pip install django-webix

Configure
---------

Settings
~~~~~~~~

Add ``django_webix`` to your ``INSTALLED_APPS``

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


Configuration variables

.. code-block:: python

    WEBIX_LICENSE = 'PRO'  # FREE
    WEBIX_VERSION = '9.4.0'
    WEBIX_CONTAINER_ID = 'content_right'
    WEBIX_FONTAWESOME_CSS_URL = 'fontawesome/css/all.min.css'
    WEBIX_FONTAWESOME_VERSION = '5.13.1'
    WEBIX_HISTORY_ENABLE = True # optional
