Usage
==========

Install dependencies
--------------------

.. code-block::

    $ python -m pip install django-webix[commands_manager]

Configuration
-------------


Settings
~~~~~~~~

Description

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_webix.contrib.commands_manager',
        # ...
    ]

    # file where is possibile get app celery config
    DJANGO_WEBIX_COMMANDS_MANAGER_APP_CELERY = 'prjcore.celery_init'

