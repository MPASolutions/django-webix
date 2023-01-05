Quick Start
===========

Install dependencies
--------------------

.. code-block::

    $ python -m pip install django-webix[filter]


Configure
---------

Settings
~~~~~~~~

Add ``django_webix_filter`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_webix_filter',
        # ...
    ]

Add ``django-webix-filter`` URLconf to your project ``urls.py`` file

.. code-block:: python

    from django.conf.urls import url, include

    urlpatterns = [
        # ...
        url(r'^django-webix-filter/', include('django_webix_filter.urls')),
        # ...
    ]

.. warning::

    This package requires a project with ``django-webix`` setted up.


Usage
-----

Settings
~~~~~~~~

.. code-block:: python

    from django.utils.translation import gettext_lazy as _

    DJANGO_WEBIX_FILTER = {
        'models': {
            'myapp.mymodel': {
                'fields': ['field1', 'field2', '...', 'fieldN'],
                'initial': True  # default value if not specified
            },
            'myapp.myothermodel': {'initial': False},
        },
        'visibility': {  # Default filter visibility
            'Group1': {
                'default': FilterVisibility.PUBLIC
            },
            'Group2': {
                'default': FilterVisibility.PRIVATE,
                'choices': [
                    FilterVisibility.PRIVATE,
                    FilterVisibility.RESTRICTED
                ]
            },
        },
        'shared_edit_groups': {
            'Group1': {
                'default': True
            }
        }
    }
