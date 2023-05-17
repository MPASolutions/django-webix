import importlib
from django.apps import apps
from django.conf import settings
from django.db.models import Q, Value
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from typing import List, Dict, Any, Optional, Tuple

from django_webix.contrib.sender.models import (MessageSent, DjangoWebixSender, MessageRecipient)

CONF = getattr(settings, "WEBIX_SENDER", None)


def get_messages_read_required(request, queryset=None):
    """
    Get queryset of messages not read where reading is required

    :param request: request
    :param queryset: initial MessageRecipient queryset
    :return: queryset
    """

    if queryset is None:
        queryset = MessageRecipient.objects.all()

    # Only sent messages
    queryset = queryset.filter(message_sent__status='sent')

    # Limit filter by user
    qset = Q()
    for recipient_config in CONF['recipients']:
        app_label, model = recipient_config['model'].lower().split(".")
        model_class = apps.get_model(app_label=app_label, model_name=model)
        recipient_queryset = model_class.objects.all()
        recipient_queryset = recipient_queryset.select_related(*model_class.get_select_related())
        recipient_queryset = recipient_queryset.prefetch_related(*model_class.get_prefetch_related())
        recipient_queryset = recipient_queryset.filter(
            model_class.get_filters_viewers(request.user, request=request)
        )
        qset |= Q(**{"{}_message_recipients__in".format(model): recipient_queryset})
    queryset = queryset.filter(qset)

    # filter for read required
    send_methods_read_required = []
    for send_method in CONF['send_methods']:
        if send_method.get('read_required', False):
            send_methods_read_required.append(send_method['function'])
    queryset = queryset.filter(Q(message_sent__send_method__in=send_methods_read_required) | \
                               Q(message_sent__typology__read_required=True) | \
                               Q(message_sent__read_required=True) )

    # get only not read messages
    queryset = queryset.exclude(message_sent__messageuserread__user_id=Value(request.user.pk))
    return queryset.distinct().order_by('-creation_date')


def my_import(name: str) -> callable:
    """
    Load a function from a string

    :param name: function path name (e.g. django_webix.contrib.sender.send_methods.email.send_utils)
    :return: callable
    """

    module, function = name.rsplit('.', 1)
    component = importlib.import_module(module)
    return getattr(component, function)


def send_mixin(send_method: str, typology: Optional[int], subject: str, body: str, recipients: Dict[str, List[int]],
               presend: Optional[Any], **kwargs) -> Tuple[Dict[str, Any], int]:
    """
    Function to send the message

    :param send_method: <skebby|email|telegram|storage>.<function> (eg. "skebby.django_webix.contrib.sender.send_methods.email.send_utils")
    :param typology: MessageTypology ID
    :param subject: Subject of message
    :param body: Body of message (email, skebby, telegram or storage)
    :param recipients: Dict {'<app_label>.<model>': [<id>, <id>]}
    :param presend: None: verify before the send; Otherwise: send the message
    :param kwargs: `user` and `files` (default: user=None, files={})
    :return: Tuple[Dict, Code]
    """

    user = kwargs.get('user')
    files = kwargs.get('files', {})

    # 1.a Recupero la lista delle istanze a cui inviare il messaggio (modello, lista destinatari)
    _recipients_instance = []
    for key, value in recipients.items():
        app_label, model = key.lower().split(".")
        model_class = apps.get_model(app_label=app_label, model_name=model)
        if not issubclass(model_class, DjangoWebixSender):
            raise Exception('{}.{} is not subclass of `DjangoWebixSender`'.format(app_label, model))
        _recipients_instance += list(model_class.objects.filter(pk__in=value))
    _recipients_instance = list(set(_recipients_instance))

    # 1.b Recupero i contatti collegati ai destinatari principali
    for _recipient in _recipients_instance:
        if hasattr(_recipient, 'get_sms_related'):
            for related in _recipient.get_sms_related:
                if not issubclass(related.__class__, DjangoWebixSender):
                    raise Exception(_('Related is not subclass of `DjangoWebixSender`'))
                _recipients_instance.append(related)
        if hasattr(_recipient, 'get_email_related'):
            for related in _recipient.get_email_related:
                if not issubclass(related.__class__, DjangoWebixSender):
                    raise Exception(_('Related is not subclass of `DjangoWebixSender`'))
                _recipients_instance.append(related)
        if hasattr(_recipient, 'get_telegram_related'):
            for related in _recipient.get_telegram_related:
                if not issubclass(related.__class__, DjangoWebixSender):
                    raise Exception(_('Related is not subclass of `DjangoWebixSender`'))
                _recipients_instance.append(related)
    _recipients_instance = list(set(_recipients_instance))

    # 2. Recupero la funzione per inviare
    method, function = send_method.split(".", 1)

    # Recupero le impostazioni per questo metodo
    send_method_conf = None
    for _send_method in CONF['send_methods']:
        if _send_method['method'] == method and _send_method['function'] == function:
            send_method_conf = _send_method
    if send_method_conf is None:
        return {'status': _('Invalid send method')}, 400

    # 3. Creo dizionario dei destinatari
    _recipients = {
        'valids': {
            'recipients': [],
            'address': []
        },
        'duplicates': {
            'recipients': [],
            'address': []
        },
        'invalids': {
            'recipients': [],
            'address': []
        }
    }
    recipients_clean = my_import(send_method_conf['recipients_clean'])
    recipients_clean(_recipients_instance, _recipients)

    # Convert dict in list of tuples
    _recipients['valids'] = list(zip(_recipients['valids']['recipients'], _recipients['valids']['address']))
    _recipients['duplicates'] = list(
        zip(_recipients['duplicates']['recipients'], _recipients['duplicates']['address'])
    )
    _recipients['invalids'] = list(zip(_recipients['invalids']['recipients'], _recipients['invalids']['address']))

    # 4 Verifica prima dell'invio (opzionale)
    if presend is None:
        presend_check = my_import(send_method_conf['presend_check'])
        result = presend_check(subject, body)
        if result is not None:
            return result
        return {
            'valids': len(_recipients['valids']),
            'duplicates': len(_recipients['duplicates']),
            'invalids': len(_recipients['invalids'])
        }, 200

    # 5. Creo istanza `MessageAttachment` senza collegarlo alla m2m -> da collegare al passo 5
    attachments = my_import(CONF['attachments']['save_function'])(
        files,
        send_method=send_method,
        typology=typology,
        subject=subject,
        body=body,
        recipients=_recipients
    )

    # 6. aggiungo il link del file in fondo al corpo
    if len(attachments) > 0:
        attachments_format = my_import(send_method_conf['attachments_format'])
        result = attachments_format(attachments, body)
        if result is not None:
            body = result

    # 7. Creo il log e collego gli allegati
    # Costo del messaggio
    _cost = 0
    if hasattr(user, 'get_cost'):
        _cost = user.get_cost(send_method)

    # Mittente del messaggio
    _sender = None
    if hasattr(user, 'get_sender'):
        _sender = user.get_sender()

    message_sent = MessageSent(
        send_method=send_method,
        subject=subject,
        body=body,
        cost=_cost,
        user=user,
        sender=_sender
    )
    #if CONF['typology_model']['enabled']:
    message_sent.typology_id = typology

    message_sent.save()
    message_sent.attachments.add(*attachments)

    # 8. Send messages
    send_function = my_import(function)
    result = send_function(_recipients, subject, body, message_sent)
    status = format_lazy('{method} sent', method=method.capitalize())

    # Add optional extra params
    if kwargs.get('extra') is not None and isinstance(kwargs.get('extra'), dict):
        if result.extra is None:
            result.extra = {}
        result.extra.update(kwargs.get('extra'))
        result.save()

    return {'status': status, 'extra': result.extra}, 200
