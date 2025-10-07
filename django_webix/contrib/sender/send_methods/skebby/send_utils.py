from typing import Dict, List

import phonenumbers
import six
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_webix.contrib.sender.send_methods.skebby.enums import SkebbyBoolean
from django_webix.contrib.sender.send_methods.skebby.exceptions import SkebbyException
from django_webix.contrib.sender.send_methods.skebby.gateway import Skebby

# https://en.wikipedia.org/wiki/GSM_03.38#GSM_7-bit_default_alphabet_and_extension_table_of_3GPP_TS_23.038_.2F_GSM_03.38
# ESC is an Escape to extension table (maps to NBSP).
# FF is a Page Break control. If not recognized, it shall be treated like LF.
# CR2 is a control character. No language specific character shall be encoded at this position.
# SS2 is a second Single Shift Escape control reserved for future extensions.
GSM_7_BIT = [
    # Basic Character Set
    "@",
    "Δ",
    " ",
    "0",
    "¡",
    "P",
    "¿",
    "p",
    "£",
    "_",
    "!",
    "1",
    "A",
    "Q",
    "a",
    "q",
    "$",
    "Φ",
    '"',
    "2",
    "B",
    "R",
    "b",
    "r",
    "¥",
    "Γ",
    "#",
    "3",
    "C",
    "S",
    "c",
    "s",
    "è",
    "Λ",
    "¤",
    "4",
    "D",
    "T",
    "d",
    "t",
    "é",
    "Ω",
    "%",
    "5",
    "E",
    "U",
    "e",
    "u",
    "ù",
    "Π",
    ";",
    "6",
    "F",
    "V",
    "f",
    "v",
    "ì",
    "Ψ",
    "'",
    "7",
    "G",
    "W",
    "g",
    "w",
    "ò",
    "Σ",
    "(",
    "8",
    "H",
    "X",
    "h",
    "x",
    "Ç",
    "Θ",
    ")",
    "9",
    "I",
    "Y",
    "i",
    "y",
    "\n",
    "Ξ",
    "*",
    ":",
    "J",
    "Z",
    "j",
    "z",
    "Ø",
    "ESC",
    "+",
    ";",
    "K",
    "Ä",
    "k",
    "ä",
    "ø",
    "Æ",
    ",",
    ";",
    "L",
    "Ö",
    "l",
    "ö",
    "\r",
    "æ",
    "-",
    "=",
    "M",
    "Ñ",
    "m",
    "ñ",
    "Å",
    "ß",
    ".",
    ";",
    "N",
    "Ü",
    "n",
    "ü",
    "å",
    "É",
    "/",
    "?",
    "O",
    "§",
    "o",
    "à",
    # Basic Character Set Extension
    "|",
    "^",
    "€",
    "{",
    "}",
    "FF",
    "SS2",
    "[",
    "CR2",
    "~",
    "]",
    "\\",
]


def check_config_skebby(config_skebby):
    assert isinstance(config_skebby, dict), "The skebby configuration must be a dictionary"
    assert "region" in config_skebby, "Missing key region in the configuration"
    assert "method" in config_skebby, "Missing key method in the configuration"
    assert "username" in config_skebby, "Missing key username in the configuration"
    assert "password" in config_skebby, "Missing key password in the configuration"
    assert "sender_string" in config_skebby, "Missing key sender_string in the configuration"
    assert "cost" in config_skebby, "Missing key cost in the configuration"


def send(recipients: Dict[str, List[int]], subject: str, body: str, message_sent, request=None):
    """
    Send Sebby sms

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

    result = {"status": "failed"}  # Default failed, change later if sent successfully
    sent_per_recipient = 0

    try:
        config_skebby = get_config_from_settings("skebby", request)
        check_config_skebby(config_skebby)

        # Connection
        skebby = Skebby()
        skebby.authentication.session_key(username=config_skebby["username"], password=config_skebby["password"])

        # Set message configuration
        send_configuration = {
            "message_type": config_skebby["method"],
            "message": body,
            "recipient": [number for _, number in recipients["valids"]],
            "sender": config_skebby["sender_string"],
            "return_credits": SkebbyBoolean.TRUE,
        }
        if "encoding" in config_skebby:
            send_configuration["encoding"] = config_skebby["encoding"]
        if "truncate" in config_skebby:
            send_configuration["truncate"] = config_skebby["truncate"]
        if "max_fragments" in config_skebby:
            send_configuration["max_fragments"] = config_skebby["max_fragments"]
        if "allow_invalid_recipients" in config_skebby:
            send_configuration["allow_invalid_recipients"] = config_skebby["allow_invalid_recipients"]

        # Send message
        result = skebby.sms_send.send_sms(**send_configuration)
        result["status"] = "success"
    except SkebbyException as e:
        result["error"] = "{}".format(e)

    # Set the order number to later retrieve the status of various messages
    if result["status"] == "success" and "total_sent" in result:
        sent_per_recipient = int(result["total_sent"]) / len(recipients["valids"])

    # For each user with a number, create a record
    for recipient, recipient_address in recipients["valids"]:
        message_recipient = MessageRecipient(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=sent_per_recipient,
            status="unknown" if result["status"] == "success" else "failed",  # Sconosciuto se con successo
            recipient_address=recipient_address,
        )
        message_recipient.save()

    # Save recipients without a number and therefore to whom the message was not sent
    for recipient, recipient_address in recipients["invalids"]:
        message_recipient = MessageRecipient(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=0,
            status="invalid",
            recipient_address=recipient_address or "invalid",
            extra={
                "status": "Mobile number not present or not valid ({}) and therefore SMS not sent".format(recipient)
            },
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
            extra={"status": "Mobile number duplicated ({})".format(recipient)},
        )
        message_recipient.save()

    message_sent.extra = result
    message_sent.save()

    return message_sent


def recipients_clean(recipients_instance, recipients, request=None):
    from django_webix.contrib.sender.utils import get_config_from_settings

    config_skebby = get_config_from_settings("skebby", request)
    check_config_skebby(config_skebby)

    for recipient in recipients_instance:
        # Retrieve the phone number and put it in a list if it's not already a list
        _get_sms = recipient.get_sms
        if not isinstance(_get_sms, list):
            _get_sms = [_get_sms]

        # For each number, verify its status and add it to the correct key
        for _sms in _get_sms:
            # Verify that the number is valid
            try:
                number = phonenumbers.parse(_sms, config_skebby["region"])
                _sms = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
                # Contact not yet present in the list
                if phonenumbers.is_valid_number(number) and _sms not in recipients["valids"]["address"]:
                    recipients["valids"]["address"].append(_sms)
                    recipients["valids"]["recipients"].append(recipient)
                # Contact already present in the list (duplicate)
                elif phonenumbers.is_valid_number(number):
                    recipients["duplicates"]["address"].append(_sms)
                    recipients["duplicates"]["recipients"].append(recipient)
                # Address not present or invalid
                else:
                    raise Exception("Invalid number")
            except Exception:
                recipients["invalids"]["address"].append(_sms)
                recipients["invalids"]["recipients"].append(recipient)


def presend_check(subject, body):
    # Verify that the body of the SMS is valid
    invalid_characters = ""
    for c in body:
        if c not in GSM_7_BIT:
            invalid_characters += c
    if invalid_characters != "":
        return {"status": _("Invalid characters"), "data": invalid_characters}, 400


def attachments_format(attachments, body):
    body += "\n\n"
    for attachment in attachments:
        body += "{attachment}\n".format(attachment=attachment.get_url())
    return body
