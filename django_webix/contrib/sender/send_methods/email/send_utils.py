from typing import Dict, List

import six
from django.conf import settings
from django.core.mail import EmailMessage


def send(recipients: Dict[str, List[int]], subject: str, body: str, message_sent):
    """
    Send email

    :param recipients: Dict {'<app_label>.<model>': [<id>, <id>]}
    :param subject: Subject of email
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
    if not isinstance(subject, six.string_types):
        raise Exception("`subject` must be a string")
    if not isinstance(body, six.string_types):
        raise Exception("`body` must be a string")
    if not isinstance(message_sent, MessageSent):
        raise Exception("`message_sent` must be MessageSent instance")

    CONFIG_EMAIL = next(
        (item for item in settings.WEBIX_SENDER['send_methods'] if item["method"] == "email"), {}
    ).get("config")

    # Per ogni istanza di destinatario ciclo
    for recipient, recipient_address in recipients['valids']:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=CONFIG_EMAIL['from_email'],
            to=[recipient_address]
        )
        email.content_subtype = "html"

        try:
            email.send()

            _extra = {'status': "Email {} ({}) inviata con successo".format(recipient_address, recipient)}
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
            extra={'status': "Email non presente ({}) e quindi non inviata".format(recipient)}
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
            extra={'status': "Email duplicata".format(recipient)}
        )
        message_recipient.save()

    return message_sent


def recipients_clean(recipients_instance, recipients):
    for recipient in recipients_instance:
        # Prelevo l'indirizzo email e lo metto in una lista se non è già una lista
        _get_email = recipient.get_email
        if not isinstance(_get_email, list):
            _get_email = [_get_email]

        # Per ogni email verifico il suo stato e lo aggiungo alla chiave corretta
        for _email in _get_email:
            # Contatto non ancora presente nella lista
            if _email and not _email in recipients['valids']['address']:
                recipients['valids']['address'].append(_email)
                recipients['valids']['recipients'].append(recipient)
            # Contatto già presente nella lista (duplicato)
            elif _email:
                recipients['duplicates']['address'].append(_email)
                recipients['duplicates']['recipients'].append(recipient)
            # Indirizzo non presente
            else:
                recipients['invalids']['address'].append(_email)
                recipients['invalids']['recipients'].append(recipient)


def presend_check(subject, body):
    pass


def attachments_format(attachments, body):
    body += "</br></br>"
    for attachment in attachments:
        body += "<a href='{attachment}'>{attachment}</a></br>".format(attachment=attachment.get_url())
    return body
