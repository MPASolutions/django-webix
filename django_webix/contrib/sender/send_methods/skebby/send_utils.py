
from typing import Dict, List

import phonenumbers
import six
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from django_webix.contrib.sender.send_methods.skebby.enums import SkebbyBoolean
from django_webix.contrib.sender.send_methods.skebby.exceptions import SkebbyException
from django_webix.contrib.sender.send_methods.skebby.gateway import Skebby

ISO_8859_1_limited = '@èéùìò_ !"#%\\\'()*+,-./0123456789:<=>?ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜabcdefghijklmnopqrstuvwxyzäöñüà'


def send(recipients: Dict[str, List[int]], subject: str, body: str, message_sent):
    """
    Send Sebby sms

    :param recipients: Dict {'<app_label>.<model>': [<id>, <id>]}
    :param body: Body of message
    :param message_sent: MessageSent instance
    :return: MessageSent instance
    """

    from django_webix.contrib.sender.models import MessageRecipient, MessageSent

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

    result = {'status': 'failed'}  # Default failed, cambia poi se inviato con successo
    sent_per_recipient = 0

    try:
        CONFIG_SKEBBY = next(
            (item for item in settings.WEBIX_SENDER['send_methods'] if item["method"] == "skebby"), {}
        ).get("config")

        # Connection
        skebby = Skebby()
        skebby.authentication.session_key(
            username=CONFIG_SKEBBY['username'],
            password=CONFIG_SKEBBY['password']
        )

        # Set message configuration
        send_configuration = {
            "message_type": CONFIG_SKEBBY['method'],
            "message": body,
            "recipient": [number for _, number in recipients['valids']],
            "sender": CONFIG_SKEBBY['sender_string'],
            "return_credits": SkebbyBoolean.TRUE
        }
        if 'encoding' in CONFIG_SKEBBY:
            send_configuration['encoding'] = CONFIG_SKEBBY['encoding']
        if 'truncate' in CONFIG_SKEBBY:
            send_configuration['truncate'] = CONFIG_SKEBBY['truncate']
        if 'max_fragments' in CONFIG_SKEBBY:
            send_configuration['max_fragments'] = CONFIG_SKEBBY['max_fragments']
        if 'allow_invalid_recipients' in CONFIG_SKEBBY:
            send_configuration['allow_invalid_recipients'] = CONFIG_SKEBBY['allow_invalid_recipients']

        # Send message
        result = skebby.sms_send.send_sms(**send_configuration)
        result['status'] = 'success'
    except SkebbyException as e:
        result['error'] = '{}'.format(e)

    # Setto il numero dell'ordine per recuperare successivamente lo stato dei vari messaggi
    if result['status'] == 'success' and 'total_sent' in result:
        sent_per_recipient = int(result['total_sent']) / len(recipients['valids'])

    # Per ogni utente con numero creo un record
    for recipient, recipient_address in recipients['valids']:
        _result = ""
        message_recipient = MessageRecipient(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=sent_per_recipient,
            status='unknown' if result['status'] == 'success' else 'failed',  # Sconosciuto se con successo
            recipient_address=recipient_address
        )
        message_recipient.save()

    # Salvo i destinatari senza numero e quindi ai quali non è stato inviato il messaggio
    for recipient, recipient_address in recipients['invalids']:
        message_recipient = MessageRecipient(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=0,
            status='invalid',
            recipient_address=recipient_address,
            extra={'status': "Mobile number not present or not valid ({}) and therefore SMS not sent".format(recipient)}
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
            extra={'status': "Mobile number duplicated ({})".format(recipient)}
        )
        message_recipient.save()

    message_sent.extra = result
    message_sent.save()

    return message_sent


def recipients_clean(recipients_instance, recipients):
    CONFIG_SKEBBY = next(
        (item for item in settings.WEBIX_SENDER['send_methods'] if item["method"] == "skebby"), {}
    ).get("config")

    for recipient in recipients_instance:
        # Prelevo il numero di telefono e lo metto in una lista se non è già una lista
        _get_sms = recipient.get_sms
        if not isinstance(_get_sms, list):
            _get_sms = [_get_sms]

        # Per ogni numero verifico il suo stato e lo aggiungo alla chiave corretta
        for _sms in _get_sms:
            # Verifico che il numero sia valido
            try:
                number = phonenumbers.parse(_sms, CONFIG_SKEBBY['region'])
                _sms = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
                # Contatto non ancora presente nella lista
                if phonenumbers.is_valid_number(number) and _sms not in recipients['valids']['address']:
                    recipients['valids']['address'].append(_sms)
                    recipients['valids']['recipients'].append(recipient)
                # Contatto già presente nella lista (duplicato)
                elif phonenumbers.is_valid_number(number):
                    recipients['duplicates']['address'].append(_sms)
                    recipients['duplicates']['recipients'].append(recipient)
                # Indirizzo non presente o non valido
                else:
                    raise Exception("Invalid number")
            except Exception:
                recipients['invalids']['address'].append(_sms)
                recipients['invalids']['recipients'].append(recipient)


def presend_check(subject, body):
    # Verifico che il corpo dell'sms sia valido
    invalid_characters = ''
    for c in body:
        if c not in ISO_8859_1_limited:
            invalid_characters += c
    if invalid_characters != '':
        return {'status': _('Invalid characters'), 'data': invalid_characters}, 400


def attachments_format(attachments, body):
    body += "\n\n"
    for attachment in attachments:
        body += "{attachment}\n".format(attachment=attachment.get_url())
    return body
