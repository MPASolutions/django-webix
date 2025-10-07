from typing import Dict, List

import six
from django.conf import settings
from django.core.mail import EmailMessage, get_connection


def send(recipients: Dict[str, List[int]], subject: str, body: str, message_sent, request=None):
    """
    Send email

    :param recipients: Dict {'<app_label>.<model>': [<id>, <id>]}
    :param subject: Subject of email
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
    if not isinstance(subject, six.string_types):
        raise Exception("`subject` must be a string")
    if not isinstance(body, six.string_types):
        raise Exception("`body` must be a string")
    if not isinstance(message_sent, MessageSent):
        raise Exception("`message_sent` must be MessageSent instance")

    config_email = get_config_from_settings("email", request)

    mail_connection = get_connection(
        backend=config_email.get("backend"),
        fail_silently=config_email.get("fail_silently", False),
        **config_email.get("backend_arguments", {})
    )

    # For each recipient instance, loop through
    for recipient, recipient_address in recipients["valids"]:

        email = EmailMessage(
            connection=mail_connection,
            subject=subject,
            body=body,
            from_email=config_email["from_email"],
            to=[recipient_address],
        )
        email.content_subtype = "html"

        try:
            email.send()

            _extra = {"status": "Email {} ({}) inviata con successo".format(recipient_address, recipient)}
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
            recipient_address=recipient_address or "",
            extra={"status": "Email non presente ({}) e quindi non inviata".format(recipient)},
        )
        message_recipient.save()

    # Save duplicate recipients and therefore to whom the message was not sent
    for recipient, recipient_address in recipients["duplicates"]:
        message_recipient = MessageRecipient(
            message_sent=message_sent,
            recipient=recipient,
            sent_number=0,
            status="duplicate",
            recipient_address=recipient_address or "",
            extra={"status": "Email duplicata {}".format(recipient)},
        )
        message_recipient.save()

    return message_sent


def recipients_clean(recipients_instance, recipients, request=None):
    for recipient in recipients_instance:
        # Retrieve the email address and put it in a list if it's not already a list
        _get_email = recipient.get_email
        if not isinstance(_get_email, list):
            _get_email = [_get_email]

        # For each email, verify its status and add it to the correct key
        for _email in _get_email:
            # Contact not yet present in the list
            if _email and _email not in recipients["valids"]["address"]:
                recipients["valids"]["address"].append(_email)
                recipients["valids"]["recipients"].append(recipient)
            # Contact already present in the list (duplicate)
            elif _email:
                recipients["duplicates"]["address"].append(_email)
                recipients["duplicates"]["recipients"].append(recipient)
            # Address not present
            else:
                recipients["invalids"]["address"].append(_email)
                recipients["invalids"]["recipients"].append(recipient)


def presend_check(subject, body):
    pass


def attachments_format(attachments, body):
    body += "<br/><br/>"
    for attachment in attachments:
        body += "<a href='{attachment}'>{attachment}</a><br/>".format(attachment=attachment.get_url())
    return body
