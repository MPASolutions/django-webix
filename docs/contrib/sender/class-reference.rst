Class Reference
===============

Models
------
.. autofunction:: django_webix_sender.models.save_attachments
.. autoclass:: django_webix_sender.models.DjangoWebixSender
    :members:
.. autoclass:: django_webix_sender.models.Customer
    :members:
.. autoclass:: django_webix_sender.models.CustomerTypology
    :members:
.. autoclass:: django_webix_sender.models.ExternalSubject
    :members:
.. autoclass:: django_webix_sender.models.ExternalSubjectTypology
    :members:
.. autoclass:: django_webix_sender.models.MessageAttachment
    :members:
.. autoclass:: django_webix_sender.models.MessageTypology
    :members:
.. autoclass:: django_webix_sender.models.MessageSent
    :members:
.. autoclass:: django_webix_sender.models.MessageRecipient
    :members:
.. autoclass:: django_webix_sender.models.MessageUserRead
    :members:
.. autoclass:: django_webix_sender.models.TelegramPersistence
    :members:

Template Tags
-------------
.. automodule:: django_webix_sender.templatetags.field_type
   :members:
.. automodule:: django_webix_sender.templatetags.send_methods_utils
   :members:
.. automodule:: django_webix_sender.templatetags.verbose_name
   :members:

Views
-----
.. autoclass:: django_webix_sender.views.SenderListView
    :members:
.. autoclass:: django_webix_sender.views.SenderGetListView
    :members:
.. autoclass:: django_webix_sender.views.SenderSendView
    :members:
.. autoclass:: django_webix_sender.views.SenderWindowView
    :members:
.. autoclass:: django_webix_sender.views.SenderMessagesListView
    :members:
.. autoclass:: django_webix_sender.views.SenderMessagesChatView
    :members:
.. autoclass:: django_webix_sender.views.SenderInvoiceManagementView
    :members:
.. autoclass:: django_webix_sender.views.SenderTelegramWebhookView
    :members:

Utils
-----
.. autofunction:: django_webix_sender.utils.my_import
.. autofunction:: django_webix_sender.utils.send_mixin


Send Methods
------------

Email
~~~~~

Send Utils
__________
.. automodule:: django_webix_sender.send_methods.email.send_utils
   :members:

Skebby
~~~~~~

Enums
_____
.. automodule:: django_webix_sender.send_methods.skebby.enums
   :members:

Exceptions
__________
.. automodule:: django_webix_sender.send_methods.skebby.exceptions
   :members:

Gateway
_______
.. automodule:: django_webix_sender.send_methods.skebby.gateway
   :members:

Send Utils
__________
.. automodule:: django_webix_sender.send_methods.skebby.send_utils
   :members:

Tasks
_____
.. automodule:: django_webix_sender.send_methods.skebby.tasks
   :members:

Storage
~~~~~~~

Send Utils
__________

.. automodule:: django_webix_sender.send_methods.storage.send_utils
   :members:

Telegram
~~~~~~~~

Handlers
________
.. automodule:: django_webix_sender.send_methods.telegram.handlers
   :members:

Persistence
___________
.. automodule:: django_webix_sender.send_methods.telegram.persistences
   :members:

Send Utils
__________
.. automodule:: django_webix_sender.send_methods.telegram.send_utils
   :members:
