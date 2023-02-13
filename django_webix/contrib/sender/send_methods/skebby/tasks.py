
from celery import shared_task
from django.conf import settings

from django_webix.contrib.sender.send_methods.skebby.exceptions import SkebbyException
from django_webix.contrib.sender.send_methods.skebby.gateway import Skebby


@shared_task
def check_state(order_id):
    from django_webix.contrib.sender.models import MessageSent

    if 'django_webix.contrib.sender' not in settings.INSTALLED_APPS:
        raise Exception("Django Webix Sender is not in INSTALLED_APPS")

    try:
        message_sent = MessageSent.objects.get(extra__order_id=order_id)
    except MessageSent.DoesNotExist:
        return {'status': 'Invalid order id'}

    try:
        CONFIG_SKEBBY = next(
            (item for item in settings.WEBIX_SENDER['send_methods'] if item["method"] == "skebby"), {}
        ).get("config")

        skebby = Skebby()
        skebby.authentication.session_key(
            username=CONFIG_SKEBBY['username'],
            password=CONFIG_SKEBBY['password']
        )

        if message_sent.messagerecipient_set.filter(status='unknown').exists():
            response = skebby.sms_send.get_sms_state(order_id)

            for recipient in response['recipients']:
                _recipients = message_sent.messagerecipient_set.filter(
                    recipient_address=recipient['destination'],
                    status='unknown'
                )
                for r in _recipients:
                    if recipient['status'] in ['SENT', 'DLVRD']:
                        r.status = 'success'
                    elif recipient['status'] in ['WAITING', 'WAIT4DLVR', 'SCHEDULED']:
                        r.status = 'unknown'
                    else:
                        r.status = 'failed'
                    r.extra = recipient
                    r.save()
                message_sent.save()
            if not message_sent.messagerecipient_set.filter(status='unknown').exists():
                return {'status': 'all_updated'}
        else:
            return {'status': 'all_updated'}
        return {'status': 'incomplete'}
    except SkebbyException as e:
        return {'status': e}


@shared_task
def check_state_history(same_sender_name=True):
    if 'django_webix.contrib.sender' not in settings.INSTALLED_APPS:
        raise Exception("Django Webix Sender is not in INSTALLED_APPS")

    from django_webix.contrib.sender.models import MessageRecipient

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

        # Recupero tutti i destinatari con stato unknown
        recipients = MessageRecipient.objects.filter(
            message_sent__send_method='skebby.django_webix.contrib.sender.send_methods.skebby.send',
            status='unknown'
        ).values_list('recipient_address', flat=True).order_by().distinct()

        # Ciclo sui singoli destinatari
        for recipient in recipients:
            # Recupero il messaggio più vecchio di questo destinatario
            date_from = MessageRecipient.objects.filter(
                message_sent__send_method='skebby.django_webix.contrib.sender.send_methods.skebby.send',
                status='unknown',
                recipient_address=recipient
            ).values_list('creation_date', flat=True).order_by('creation_date').first()

            results = skebby.sms_history.get_sent_sms_to_recipient(
                recipient=recipient,
                date_from=date_from.strftime("%Y%m%d000000"),
                page_size=1000
            )

            for communication in results['rcpthistory']:
                if same_sender_name is True and communication['sender'] != CONFIG_SKEBBY['sender_string']:
                    continue

                # Estraggo la comunicazione con lo stesso order_id
                message_recipient = MessageRecipient.objects.filter(
                    message_sent__send_method='skebby.django_webix.contrib.sender.send_methods.skebby.send',
                    message_sent__extra__order_id=communication['order_id'],
                    status='unknown',
                    recipient_address=recipient,
                )

                # 2 = In attesa
                # 4 = OK
                # 9 = Errore generico
                # 10 = Messaggio scaduto
                if communication['status'] == 4:
                    message_recipient.update(
                        extra=communication,
                        status='success'
                    )
                elif communication['status'] in [9, 10]:
                    message_recipient.update(
                        extra=communication,
                        status='failed'
                    )
                elif communication['status'] == 2:
                    pass
                else:
                    raise SkebbyException("Status sconosciuto: {}".format(communication))

    except SkebbyException as e:
        return {'status': e}

    return {
        'remaining': MessageRecipient.objects.filter(
            message_sent__send_method='skebby.django_webix.contrib.sender.send_methods.skebby.send',
            status='unknown'
        ).only(MessageRecipient._meta.pk.name).count()
    }
