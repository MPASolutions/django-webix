from decimal import Decimal
from typing import List, Any, Dict, Union

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _

from django.db.models import JSONField

try:
    from django_dal.models import DALModel as Model
except ImportError:
    from django.db.models import Model

CONF = getattr(settings, "WEBIX_SENDER", None)


def save_attachments(files: Dict[str, Any], *args, **kwargs):
    """
    Save attachments function

    :param files: a dict with attachments
    :param args: Optional arguments
    :param kwargs: optional keyword arguments
    :return: list of MessageAttachment instances
    """

    attachments = []
    for filename, file in files.items():
        attachment = MessageAttachment.objects.create(file=file)
        attachments.append(attachment)
    return attachments


class DjangoWebixSender(Model):
    """
    Abstract model with basic configuration
    """

    message_recipients = GenericRelation('dwsender.MessageRecipient',
                                         related_query_name='%(class)s_message_recipients')

    class Meta:
        abstract = True

    @property
    def get_sms(self) -> Union[str, list]:
        """
        Get sms number

        :return: sms number
        """

        raise NotImplementedError(_("`get_sms` not implemented!"))

    @property
    def get_email(self) -> Union[str, list]:
        """
        Get email address

        :return: email address
        """

        raise NotImplementedError(_("`get_email` not implemented!"))

    @property
    def get_telegram(self) -> Union[str, list]:
        """
        Get telegram id

        :return: telegram id
        """
        raise NotImplementedError(_("`get_telegram` not implemented!"))

    @staticmethod
    def get_sms_fieldpath() -> str:
        """
        Get sms field name (or complete path with fks)

        :return: string with sms fieldname
        """

        return NotImplementedError(_("`get_sms_fieldpath` not implemented!"))

    @staticmethod
    def get_email_fieldpath() -> str:
        """
        Get email field name (or complete path with fks)

        :return: string with email fieldname
        """

        return NotImplementedError(_("`get_email_fieldpath` not implemented!"))

    @staticmethod
    def get_telegram_fieldpath() -> str:
        """
        Get telegram field name (or complete path with fks)

        :return: string with telegram fieldname
        """

        return NotImplementedError(_("`get_telegram_fieldpath` not implemented!"))

    @property
    def get_sms_related(self) -> List[Any]:
        """
        Get all sms related recipients to this instance

        :return: list of instances of related recipients
        """

        return []

    @property
    def get_email_related(self) -> List[Any]:
        """
        Get all email related recipients to this instance

        :return: list of instances of related recipients
        """

        return []

    @property
    def get_telegram_related(self) -> List[Any]:
        """
        Get all email related recipients to this instance

        :return: list of instances of related recipients
        """

        return []

    @classmethod
    def get_select_related(cls) -> List[str]:
        """
        Related field to optimize django queries

        :return: list of select related fields
        """

        return []

    @classmethod
    def get_prefetch_related(cls) -> List[str]:
        """
        Related field to optimize django queries

        :return: list of prefetch related fields
        """

        return []

    @classmethod
    def get_filters_viewers(cls, user, *args, **kwargs) -> Q:
        """
        Filters recipients that can be seen by this user

        :param user: user instance
        :param args: Optional arguments
        :param kwargs: optional keyword arguments
        :return: Q object with filters
        """

        return NotImplementedError(_("`get_filters_viewers` not implemented!"))

    @classmethod
    def get_representation(cls) -> F:
        """
        Get field to create a sql rapresentation

        :return: F object
        """

        return NotImplementedError(_("`get_representation` not implemented!"))


class CustomerTypology(Model):
    """
    Customer typology model
    """

    typology = models.CharField(max_length=255, unique=True, verbose_name=_('Typology'))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('Modification data'))

    class Meta:
        verbose_name = _('Customer typology')
        verbose_name_plural = _('Customer typologies')

    def __str__(self):
        return '{}'.format(self.typology)


class Customer(DjangoWebixSender):
    """
    Customer model
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                             verbose_name=_('User'))
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Name'))
    vat_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Vat number'))
    fiscal_code = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Fiscal code'))
    sms = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Sms'))
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name=_('Email'))
    telegram = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Telegram'))
    note = models.TextField(blank=True, null=True, verbose_name=_('Note'))
    extra = JSONField(blank=True, null=True, verbose_name=_('Extra'))
    typology = models.ForeignKey(CustomerTypology, blank=True, null=True,
                                 on_delete=models.CASCADE, verbose_name=_('Typology'))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('Modification data'))

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def __str__(self):
        return '{}'.format(self.name)

    @property
    def get_sms(self) -> str:
        return self.sms

    @property
    def get_email(self) -> str:
        return self.email

    @property
    def get_telegram(self) -> str:
        return self.telegram

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


class ExternalSubjectTypology(Model):
    """
    External subject typology model
    """

    typology = models.CharField(max_length=255, unique=True, verbose_name=_('Typology'))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('Modification data'))

    class Meta:
        verbose_name = _('External subject typology')
        verbose_name_plural = _('External subject typologies')

    def __str__(self):
        return '{}'.format(self.typology)


class ExternalSubject(DjangoWebixSender):
    """
    External subject model
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                             verbose_name=_('User'))
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Name'))
    vat_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Vat number'))
    fiscal_code = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Fiscal code'))
    sms = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Sms'))
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name=_('Email'))
    telegram = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Telegram'))
    note = models.TextField(blank=True, null=True, verbose_name=_('Note'))
    extra = JSONField(blank=True, null=True, verbose_name=_('Extra'))
    typology = models.ForeignKey(ExternalSubjectTypology, blank=True, null=True,
                                 on_delete=models.CASCADE, verbose_name=_('Typology'))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('Modification data'))

    class Meta:
        verbose_name = _('External subject')
        verbose_name_plural = _('External subjects')

    def __str__(self):
        if self.name:
            return self.name
        else:
            return _('Not defined')

    @property
    def get_sms(self) -> str:
        return self.sms

    @property
    def get_email(self) -> str:
        return self.email

    @property
    def get_telegram(self) -> str:
        return self.telegram

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


class MessageAttachment(Model):
    """
    Message attachments model
    """

    file = models.FileField(upload_to=CONF['attachments']['upload_folder'], verbose_name=_('Document'))
    insert_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Insert date'))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('Modification data'))

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

    def __str__(self):
        return '{}'.format(self.file.name)

    def get_url(self):
        return '{}'.format(self.file.url)

    @staticmethod
    def get_file_fieldpath() -> str:
        return "file"


class MessageTypology(Model):
    """
    Message typology model
    """

    typology = models.CharField(_('Typology'), max_length=255, unique=True)
    creation_date = models.DateTimeField(_('Creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('Modification data'), auto_now=True)
    read_required = models.BooleanField(_('Read required'), blank=True, null=False, default=False)

    class Meta:
        verbose_name = _('Message typology')
        verbose_name_plural = _('Message typologies')

    def __str__(self):
        return '{}'.format(self.typology)

    @staticmethod
    def autocomplete_search_fields():
        return "typology__icontains",


class MessageTypologiesGroup(Model):
    """
    Message typologies group model
    """

    group_typologies = models.CharField(_('Group typologies'), max_length=255, unique=True)
    icon = models.CharField(_('Icon'), max_length=255, help_text='ex. "fas fa-inbox-in"')
    message_typologies = models.ManyToManyField(MessageTypology, verbose_name=_('Message typologies'))
    creation_date = models.DateTimeField(_('Creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('Modification data'), auto_now=True)

    class Meta:
        verbose_name = _('Message typologies group')
        verbose_name_plural = _('Message typologies groups')

    def __str__(self):
        return '{}'.format(self.group_typologies)

    @staticmethod
    def autocomplete_search_fields():
        return "group_typologies__icontains",


class MessageSent(Model):
    """
    Message sent model
    """

    typology = models.ForeignKey(MessageTypology,
                                     blank=True,
                                     null=True,
                                     on_delete=models.SET_NULL,
                                     verbose_name=_('Typology')
                                     )
    send_method = models.CharField(max_length=255, verbose_name=_('Send method'))
    subject = models.TextField(blank=True, null=True, verbose_name=_('Subject'))
    body = models.TextField(blank=True, null=True, verbose_name=_('Body'))
    status = models.CharField(max_length=16, choices=(
        ('sent', _('Sent')),
        ('received', _('Received')),
    ), default='sent')
    extra = JSONField(blank=True, null=True, verbose_name=_('Extra'))
    attachments = models.ManyToManyField(
        CONF['attachments']['model'],
        blank=True,
        db_constraint=False,
        verbose_name=_('Attachments')
    )
    read_required = models.BooleanField(_('Read required'), blank=True, null=False, default=False)

    # Invoice
    cost = models.DecimalField(max_digits=6, decimal_places=4, default=Decimal('0.0000'), verbose_name=_('Cost'))
    invoiced = models.BooleanField(default=False, verbose_name=_('Invoiced'))

    # Sender info
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                             verbose_name=_('User'))
    sender = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Sender'))

    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('Modification data'))

    class Meta:
        verbose_name = _('Sent message')
        verbose_name_plural = _('Sent messages')

    def __str__(self):
        return "[{}] {}".format(self.send_method, self.typology)


class MessageRecipient(Model):
    """
    Message recipient model
    """

    message_sent = models.ForeignKey(MessageSent, on_delete=models.CASCADE,
                                     verbose_name=_('Message sent'))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    recipient = GenericForeignKey('content_type', 'object_id')
    recipient_address = models.CharField(max_length=255, verbose_name=_('Recipient address'))
    sent_number = models.IntegerField(default=1, verbose_name=_('Sent number'))
    status = models.CharField(max_length=32, choices=(
        ('success', _('Success')),
        ('failed', _('Failed')),
        ('unknown', _('Unknown')),
        ('invalid', _('Invalid')),
        ('duplicate', _('Duplicate'))
    ), default='unknown')
    extra = models.TextField(blank=True, null=True, verbose_name=_('Extra'))
    extra_json = JSONField(blank=True, null=True, verbose_name=_('Extra JSON'))

    # Message status
    is_sender = models.BooleanField(blank=True, default=False)

    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('Modification data'))

    class Meta:
        verbose_name = _('Recipient')
        verbose_name_plural = _('Recipients')

    def __str__(self):
        return str(self.recipient)


class MessageUserRead(Model):
    """
    Message readed by user model
    """

    message_sent = models.ForeignKey(MessageSent, on_delete=models.CASCADE,
                                     verbose_name=_('Message sent'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'))

    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('Modification data'))

    class Meta:
        verbose_name = _('Readed message')
        verbose_name_plural = _('Readed messages')
        unique_together = (('message_sent', 'user'),)

    def __str__(self):
        return "{} {}".format(self.message_sent, self.user)


# Telegram
class TelegramPersistence(Model):
    """
    Telegram persistence model
    """

    typology = models.CharField(max_length=32, choices=[
        (i, i) for i in ['user_data', 'chat_data', 'bot_data', 'conversations']
    ], unique=True)
    data = JSONField()

    class Meta:
        verbose_name = _("Telegram Persistence")
        verbose_name_plural = _("Telegram Persistences")
