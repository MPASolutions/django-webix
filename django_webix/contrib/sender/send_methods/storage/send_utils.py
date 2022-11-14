
from typing import Dict, List

import six
from django.conf import settings


def send(recipients: Dict[str, List[int]], subject: str, body: str, message_sent):
    """
    Send email

    :param recipients: Dict {'<app_label>.<model>': [<id>, <id>]}
    :param subject: Subject of message
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

    # Per ogni istanza di destinatario ciclo
    for recipient, recipient_address in recipients['valids']:
        MessageRecipient.objects.create(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=1,
            status='success',
            recipient_address=recipient_address,
        )

    # Salvo i destinatari non validi
    for recipient, recipient_address in recipients['invalids']:
        MessageRecipient.objects.create(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=0,
            status='invalid',
            recipient_address=recipient_address,
        )

    # Salvo i destinatari duplicati
    for recipient, recipient_address in recipients['duplicates']:
        MessageRecipient.objects.create(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=0,
            status='duplicate',
            recipient_address=recipient_address,
        )

    return message_sent


def recipients_clean(recipients_instance, recipients):
    for recipient in recipients_instance:
        # Prelevo l'ID user e lo metto in una lista se non è già una lista
        if not recipient.pk in recipients['valids']['address']:
            recipients['valids']['address'].append(recipient.pk)
            recipients['valids']['recipients'].append(recipient)
        # Contatto già presente nella lista (duplicato)
        elif recipient.pk in recipients['valids']['address']:
            recipients['duplicates']['address'].append(recipient.pk)
            recipients['duplicates']['recipients'].append(recipient)
        # Indirizzo non presente
        else:
            recipients['invalids']['address'].append(recipient.pk)
            recipients['invalids']['recipients'].append(recipient)


def presend_check(subject, body):
    pass


def attachments_format(attachments, body):
    pass  # ignore this step, file already in db
