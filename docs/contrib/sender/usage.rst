Quick Start
===========

Install dependencies
--------------------

.. code-block::

    $ python -m pip install django-webix[sender]


Configure
---------

Settings
~~~~~~~~

Add ``django_webix_sender`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_webix.contrib.sender',
        # ...
    ]

Add ``django-webix-sender`` URLconf to your project ``urls.py`` file

.. code-block:: python

    from django.urls import path, include

    urlpatterns = [
        # ...
        path('django-webix-sender/', include('django_webix.contrib.sender.urls')),
        # ...
    ]

.. warning::

    This package requires a project with ``django-webix`` setted up.

.. warning::

    This package requires 'django.contrib.humanize' in ``INSTALLED_APPS``


Usage
-----

Settings
~~~~~~~~

Create the models (e.g. <app_name>/models.py)

.. code-block:: python

    from django.utils.translation import gettext_lazy as _
    from django_webix_sender.send_methods.telegram.handlers import start, check_user

    WEBIX_SENDER = {
        'send_methods': [
            {
                'method': 'skebby',
                'verbose_name': _('Send sms'),
                'function': 'django_webix.contrib.sender.send_methods.skebby.send',
                'show_in_list': True,
                'show_in_chat': False,
                'config': {
                    'region': "IT",
                    'method': SkebbyMessageType.GP,
                    'username': 'username',
                    'password': '********',
                    'sender_string': 'Sender',
                }
            },
            {
                'method': 'email',
                'verbose_name': _('Send email'),
                'function': 'django_webix.contrib.sender.send_methods.email.send',
                'show_in_list': True,
                'show_in_chat': False,
                'config': {
                    'from_email': 'noreply@email.com'
                }
            },
            {
                'method': 'telegram',
                'verbose_name': _('Send telegram'),
                'function': 'django_webix.contrib.sender.send_methods.telegram.send',
                'show_in_list': False,
                'show_in_chat': True,
                'config': {
                    "bot_token": "**********:**********",
                    "webhooks": [
                        "https://mysite.com/django-webix-sender/telegram/webhook/"
                    ],
                    'commands': [
                        BotCommand("start", "Start info"),
                    ],
                    'handlers': [
                        {"handler": MessageHandler(Filters.all, check_user), "group": -1},  # Check enabled users
                        CommandHandler("start", start),  # Example
                    ]
                }
            },
            {
                'method': 'storage',
                'verbose_name': _('Store online'),
                'function': 'django_webix.contrib.sender.send_methods.storage.send',
                'show_in_list': True,
                'show_in_chat': False,
            },
        ],
        'initial_send_methods': [
            {
                'method': 'storage',
                'function': 'django_webix.contrib.sender.send_methods.storage.send',
            },
            {
                'method': 'telegram',
                'function': 'django_webix.contrib.sender.send_methods.telegram.send',
            },
        ],
        'attachments': {
            'model': 'django_webix.contrib.sender.MessageAttachment',
            'upload_folder': 'sender/',
            'save_function': 'django_webix.contrib.sender.models.save_attachments'
        },
        'typology_model': {
            #'enabled': True,
            'required': False
        },
        'recipients': [
            {
                'model': 'django_webix.contrib.sender.Customer',
                'datatable_fields': ['user', 'name', 'sms', 'email', 'telegram'],
                'collapsed': False
            },
            {
                'model': 'django_webix.contrib.sender.ExternalSubject',
                'datatable_fields': ['user', 'name', 'sms', 'email', 'telegram'],
                'collapsed': True
            },
        ],
        'groups_can_send': ["Admin"],
        'extra': {
            'session': ['year']
        },
        'invoices_period': 'bimestrial'
    }


.. attribute:: WEBIX_SENDER['send_methods']

    Defines the allowed send methods.

    There are four allowed methods type:

    - ``skebby``

    - ``email``

    - ``telegram``

    - ``storage``


    The methods already implemented in this package are:

    - ``django_webix_sender.send_methods.email.send``

        The default Django email sender.

        .. code:: python

            {
                'method': 'email',
                'verbose_name': _('Send email'),
                'function': 'django_webix_sender.send_methods.email.send',
                'show_in_list': True,
                'show_in_chat': False,
                'config': {
                    'from_email': 'noreply@email.com'
                }
            }


    - ``django_webix_sender.send_methods.skebby.send``

        Skebby sms APIs.

        .. code:: python

            {
                'method': 'skebby',
                'verbose_name': _('Send sms with Skebby'),
                'function': 'django_webix_sender.send_methods.skebby.send',
                'show_in_list': True,
                'show_in_chat': False,
                'config': {
                    'region': "IT",
                    'method': SkebbyMessageType.GP,
                    'username': 'username',
                    'password': '********',
                    'sender_string': 'Sender',
                }
            }

    - ``django_webix_sender.send_methods.telegram.send``

        Telegram APIs.

        .. code:: python

            {
                'method': 'telegram',
                'verbose_name': _('Send with Telegram'),
                'function': 'django_webix_sender.send_methods.telegram.send',
                'show_in_list': False,
                'show_in_chat': True,
                'config': {
                    "bot_token": "**********:**********",
                    "webhooks": [
                        "https://mysite.com/django-webix-sender/telegram/webhook/"
                    ],
                    'commands': [
                        BotCommand("start", "Start info"),
                    ],
                    'handlers': [
                        {"handler": MessageHandler(Filters.all, check_user), "group": -1},  # Check enabled users
                        CommandHandler("start", start),  # Example
                    ]
                }
            }

    - ``django_webix_sender.send_methods.storage.send``

        Storage method

        .. code:: python

            {
                'method': 'storage',
                'verbose_name': _('Store online'),
                'function': 'django_webix_sender.send_methods.storage.send',
                'show_in_list': True,
                'show_in_chat': False,
            }


.. attribute:: WEBIX_SENDER['initial_send_methods']

    Optional: Defines the default send methods in the form.

    .. code-block:: python

        [
            {
                'method': 'storage',
                'function': 'django_webix.contrib.sender.send_methods.storage.send',
            },
            {
                'method': 'telegram',
                'function': 'django_webix.contrib.sender.send_methods.telegram.send',
            },
        ]


.. attribute:: WEBIX_SENDER['attachments']

    Defines the attachments model and the method to store files.

    .. code-block:: python

        {
            'model': 'django_webix.contrib.sender.MessageAttachment',
            'upload_folder': 'sender/',
            'save_function': 'django_webix.contrib.sender.models.save_attachments'
        }


.. attribute:: WEBIX_SENDER['typology_model']

    Defines if the message typology are enabled.

    .. code-block:: python

        {
            'enabled': True,
            'required': False
        }


.. attribute:: WEBIX_SENDER['recipients']

    Defines the models to show as a list of recipients.

    .. code-block:: python

        {
            'model': 'django_webix.contrib.sender.Customer',
            'datatable_fields': ['user', 'name', 'sms', 'email', 'telegram'],
            'collapsed': True
        }


.. attribute:: WEBIX_SENDER['groups_can_send']

    Optional: Defines the group names that can send messages.

    .. code-block:: python

        ["Admin"]


.. attribute:: WEBIX_SENDER['extra']

    Optional: Defines the data to add to message extra json field.
    You can define variable names in the session.

    .. code-block:: python

        {
            'session': ['year']
        }


.. attribute:: WEBIX_SENDER['invoices_period']

    Optional: Defines the periods to divide the invoices.

    The available periods are:

    - ``monthly``

    - ``bimestrial``

    - ``quarter``

    - ``half-yearly``

    - ``yearly``


.. warning::

    You can add ``get_sender`` method to the user class to indicate string to be stored in the message record

    .. code-block:: python

        def _get_sender(self):
            return self.get_full_name()

        User.get_sender = _get_sender


Base Template
~~~~~~~~~~~~~

Create a base html template (e.g. <app_name>/templates/base.html)

.. code-block:: html

    {% load i18n %}

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>

        {% include "django_webix/static_meta.html" %}
    </head>
    <body>
    </body>

    <script type="text/javascript" charset="utf-8">
        webix.ready(function () {
            webix.ui({
                id: 'content_right',
                rows: []
            });

            webix.extend($$('content_right'), webix.OverlayBox);

            load_js('{% url 'django_webix_sender.list' %}');
        });
    </script>
    </html>
