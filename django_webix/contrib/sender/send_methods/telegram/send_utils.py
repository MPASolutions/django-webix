
from typing import Dict, List

import six
import telegram
from django.conf import settings
from django.apps import apps

def send(recipients: Dict[str, List[int]], subject: str, body: str, message_sent):
    """
    Send Telegram message

    :param recipients: Dict {'<app_label>.<model>': [<id>, <id>]}
    :param body: Body of message
    :param message_sent: MessageSent instance
    :return: MessageSent instance
    """

    from django_webix.contrib.sender.models import MessageSent, MessageRecipient

    if 'django_webix.contrib.sender' not in settings.INSTALLED_APPS:
        raise Exception("Django Webix Sender is not in INSTALLED_APPS")

    # Controllo correttezza parametri
    if not isinstance(recipients, dict) or \
        'valids' not in recipients or not isinstance(recipients['valids'], list) or \
        'duplicates' not in recipients or not isinstance(recipients['duplicates'], list) or \
        'invalids' not in recipients or not isinstance(recipients['invalids'], list):
        raise Exception("`recipients` must be a dict")
    if not isinstance(body, six.string_types):
        raise Exception("`body` must be a string")
    if not isinstance(message_sent, MessageSent):
        raise Exception("`message_sent` must be MessageSent instance")

    CONFIG_TELEGRAM = next(
        (item for item in settings.WEBIX_SENDER['send_methods'] if item["method"] == "telegram"), {}
    ).get("config")

    CONF = getattr(settings, "WEBIX_SENDER", None)

    bot = telegram.Bot(token=CONFIG_TELEGRAM.get('bot_token'))

    attachments = message_sent.attachments.all()

    # Per ogni istanza di destinatario ciclo
    for recipient, recipient_address in recipients['valids']:
        try:
            bot.send_message(chat_id=recipient_address, text=body)
            for attachment in attachments:
                file = getattr(attachment, apps.get_model(CONF['attachments']['model']).get_file_fieldpath())
                if file.name.split('.')[-1] in ['jpg', 'jpeg', 'png']:
                    bot.send_photo(recipient_address, open(file.path, "rb"))
                else:
                    bot.send_document(recipient_address, open(file.path, "rb"))

            _extra = {'status': "Telegram {} ({}) inviato con successo".format(recipient_address, recipient)}
            _status = 'success'
        except Exception as e:
            _extra = {'status': "{}".format(e)}
            _status = 'failed'

        MessageRecipient.objects.create(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=1,
            status=_status,
            recipient_address=recipient_address,
            extra=_extra,
        )

    # Salvo i destinatari senza numero e quindi ai quali non è stato inviato il messaggio
    for recipient, recipient_address in recipients['invalids']:
        message_recipient = MessageRecipient(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=0,
            status='invalid',
            recipient_address=recipient_address,
            extra={'status': "Telegram non registrato ({}) e quindi non inviato".format(recipient)}
        )
        message_recipient.save()

    # Salvo i destinatari duplicati e quindi ai quali non è stato inviato il messaggio
    for recipient, recipient_address in recipients['duplicates']:
        message_recipient = MessageRecipient(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=0,
            status='duplicate',
            recipient_address=recipient_address,
            extra={'status': "Telegram duplicato".format(recipient)}
        )
        message_recipient.save()

    return message_sent


def recipients_clean(recipients_instance, recipients):
    for recipient in recipients_instance:
        # Prelevo l'ID telegram e lo metto in una lista se non è già una lista
        _get_telegram = recipient.get_telegram
        if not isinstance(_get_telegram, list):
            _get_telegram = [_get_telegram]

        # Per ogni email verifico il suo stato e lo aggiungo alla chiave corretta
        for _telegram in _get_telegram:
            # Contatto non ancora presente nella lista
            if _telegram and not _telegram in recipients['valids']['address']:
                recipients['valids']['address'].append(_telegram)
                recipients['valids']['recipients'].append(recipient)
            # Contatto già presente nella lista (duplicato)
            elif _telegram:
                recipients['duplicates']['address'].append(_telegram)
                recipients['duplicates']['recipients'].append(recipient)
            # Indirizzo non presente
            else:
                recipients['invalids']['address'].append(_telegram)
                recipients['invalids']['recipients'].append(recipient)


def presend_check(subject, body):
    pass


def attachments_format(attachments, body):
    pass  # invio fatto in send
