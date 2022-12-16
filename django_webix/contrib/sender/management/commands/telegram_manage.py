import telegram
from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import gettext_lazy as _

from django_webix.contrib.sender.models import TelegramPersistence


class Command(BaseCommand):
    help = "Telegram manage command"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(title="actions", dest="action", required=True)

        # Add webhook
        add_webhook = subparsers.add_parser("add-webhook")
        add_webhook.add_argument('url', type=str)

        # Delete webhooks
        delete_webhooks = subparsers.add_parser("delete-webhooks")

        # Clear persistence
        clear_persistence = subparsers.add_parser("clear-persistence")

    def handle(self, *args, **options):
        CONFIG_TELEGRAM = next(
            (item for item in settings.WEBIX_SENDER['send_methods'] if item["method"] == "telegram"), {}
        ).get("config")

        bot = telegram.Bot(token=CONFIG_TELEGRAM['bot_token'])

        if options.get('action') == 'delete-webhooks':
            result = bot.deleteWebhook()
            if result is True:
                self.stdout.write(_("Telegram Webhooks successfully deleted"))
            else:
                self.stdout.write(self.style.WARNING(_("Telegram Webhooks cannot be deleted")))

        elif options.get('action') == 'add-webhook':
            result = bot.setWebhook(options.get('url'))
            if result is True:
                self.stdout.write(_("Telegram Webhook successfully added"))
            else:
                self.stdout.write(self.style.WARNING(_("Telegram Webhook cannot be added")))

        elif options.get('action') == 'clear-persistence':
            result = TelegramPersistence.objects.all().delete()
            self.stdout.write(_("{} persistence elements have been deleted".format(result[0])))
