#
# NON VA!!!
# 2/10/2025 - DEPRECATO: va aggiornato tutto il SW di telegram a causa della nuova versione della libreria
#
from typing import Dict, List

import six

# noinspection PyUnresolvedReferences
import telegram
from django.apps import apps
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def send(recipients: Dict[str, List[int]], subject: str, body: str, message_sent, request=None):
    """
    Send Telegram message

    :param recipients: Dict {'<app_label>.<model>': [<id>, <id>]}
    :param body: Body of message
    :param message_sent: MessageSent instance
    :param request:
    :return: MessageSent instance
    """

    from django_webix.contrib.sender.models import MessageRecipient, MessageSent
    from django_webix.contrib.sender.utils import get_config_from_settings

    if "django_webix.contrib.sender" not in settings.INSTALLED_APPS:
        raise Exception("Django Webix Sender is not in INSTALLED_APPS")

    # Check the correctness of parameters
    if (
        not isinstance(recipients, dict)
        or "valids" not in recipients
        or not isinstance(recipients["valids"], list)
        or "duplicates" not in recipients
        or not isinstance(recipients["duplicates"], list)
        or "invalids" not in recipients
        or not isinstance(recipients["invalids"], list)
    ):
        raise Exception("`recipients` must be a dict")
    if not isinstance(body, six.string_types):
        raise Exception("`body` must be a string")
    if not isinstance(message_sent, MessageSent):
        raise Exception("`message_sent` must be MessageSent instance")

    config_telegram = get_config_from_settings("telegram", request)

    CONF = getattr(settings, "WEBIX_SENDER", None)

    bot = telegram.Bot(token=config_telegram.get("bot_token"))

    attachments = message_sent.attachments.all()

    # For each recipient instance, loop through
    for recipient, recipient_address in recipients["valids"]:
        try:
            bot.send_message(chat_id=recipient_address, text=body)
            for attachment in attachments:
                file = getattr(attachment, apps.get_model(CONF["attachments"]["model"]).get_file_fieldpath())
                if file.name.split(".")[-1] in ["jpg", "jpeg", "png"]:
                    bot.send_photo(recipient_address, open(file.path, "rb"))
                else:
                    bot.send_document(recipient_address, open(file.path, "rb"))

            _extra = {"status": _(f"Telegram {recipient_address} ({recipient}) sent successfully")}
            _status = "success"
        except Exception as e:
            _extra = {"status": "{}".format(e)}
            _status = "failed"

        MessageRecipient.objects.create(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=1,
            status=_status,
            recipient_address=recipient_address,
            extra=_extra,
        )

    # Save recipients without a number and therefore to whom the message was not sent
    for recipient, recipient_address in recipients["invalids"]:
        message_recipient = MessageRecipient(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=0,
            status="invalid",
            recipient_address=recipient_address,
            extra={"status": _(f"Telegram not registered ({recipient}) and therefore not sent")},
        )
        message_recipient.save()

    # Save duplicate recipients and therefore to whom the message was not sent
    for recipient, recipient_address in recipients["duplicates"]:
        message_recipient = MessageRecipient(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=0,
            status="duplicate",
            recipient_address=recipient_address,
            extra={"status": _(f"Telegram duplicate {recipient}")},
        )
        message_recipient.save()

    return message_sent


def recipients_clean(recipients_instance, recipients, request=None):
    for recipient in recipients_instance:
        # Retrieve the Telegram ID and put it in a list if it's not already a list
        _get_telegram = recipient.get_telegram
        if not isinstance(_get_telegram, list):
            _get_telegram = [_get_telegram]

        # For each email, verify its status and add it to the correct key
        for _telegram in _get_telegram:
            # Contact not yet present in the list
            if _telegram and _telegram not in recipients["valids"]["address"]:
                recipients["valids"]["address"].append(_telegram)
                recipients["valids"]["recipients"].append(recipient)
            # Contact already present in the list (duplicate)
            elif _telegram:
                recipients["duplicates"]["address"].append(_telegram)
                recipients["duplicates"]["recipients"].append(recipient)
            # Address not present
            else:
                recipients["invalids"]["address"].append(_telegram)
                recipients["invalids"]["recipients"].append(recipient)


def presend_check(subject, body):
    pass


def attachments_format(attachments, body):
    pass  # Sending done in send
