Customization
=============

Recipient class
---------------

| Create a subclass of ``DjangoWebixSender`` and define ``get_sms``, ``get_telegram``, ``get_email``, ``get_sms_related``, ``get_telegram_related`` and ``get_email_related`` properties, if you use that send method.
| It's important to define also ``get_email_related``, ``get_sms_fieldpath``, ``get_email_fieldpath`` and ``get_telegram_fieldpath`` classmethods.
| Optionally you can define also ``get_select_related`` and ``get_prefetch_related`` to optimize queries.
| There is also ``get_filters_viewers`` function to define which qset to apply to the recipients models to indicates their visibility.

.. code-block:: python

    class Recipients(DjangoWebixSender):
        name = models.CharField(max_length=255, verbose_name=_('Name'))
        sms = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Sms'))
        telegram = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Telegram'))
        email = models.EmailField(max_length=255, blank=True, null=True, verbose_name=_('Email'))
        parent = models.ForeignKey('self', blank=True, null=True, verbose_name=_('Parent'))

        @property
        def get_sms(self):
            return self.sms

        @property
        def get_telegram(self):
            return self.telegram

        @property
        def get_email(self):
            return self.email

        @property
        def get_sms_related(self):
            return self.parent_set.all()

        @property
        def get_telegram_related(self):
            return self.parent_set.all()

        @property
        def get_email_related(self):
            return self.parent_set.all()

        @staticmethod
        def get_sms_fieldpath() -> str:
            return "sms"

        @staticmethod
        def get_email_fieldpath() -> str:
            return "email"

        @staticmethod
        def get_telegram_fieldpath() -> str:
            return "telegram"

        @classmethod
        def get_filters_viewers(cls, user, *args, **kwargs) -> Q:
            if user is None:
                return Q(pk__isnull=True)  # Fake filter, empty queryset
            if user.is_anonymous:
                return Q(pk__isnull=True)  # Fake filter, empty queryset
            if not user.is_superuser:
                return Q(user=user)
            return Q()  # Non filters

        @classmethod
        def get_representation(cls) -> F:
            return F('name')


.. warning::

    You need to define ``get_filters_viewers`` staticmethod to the recipient models to filter recipients that can be
    seen by passed user.
    This method must returns QSet object.

    .. code-block:: python

        @classmethod
        def get_filters_viewers(cls, user, *args, **kwargs) -> Q:
            if user is None:
                return Q(pk__isnull=True)  # Fake filter, empty queryset
            if user.is_anonymous:
                return Q(pk__isnull=True)  # Fake filter, empty queryset
            if not user.is_superuser:
                return Q(user=user)
            return Q()  # Non filters


Send method
-----------

.. code-block:: python

    def send_sms(recipients, body, message_sent):

        # ...
        # API gateway sms send
        # ...

        for recipient, recipient_address in recipients['valids']:
            MessageRecipient.objects.create(
                message_sent=message_sent,
                recipient=recipient,
                sent_number=1,
                status='success',
                recipient_address=recipient_address
            )
        for recipient, recipient_address in recipients['invalids']:
            pass  # You must create MessageRecipient instance
        for recipient, recipient_address in recipients['duplicates']:
            pass  # You must create MessageRecipient instance
        return message_sent
