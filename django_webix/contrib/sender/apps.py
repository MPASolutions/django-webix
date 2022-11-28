import telegram
from django.apps import AppConfig
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


class SenderConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "django_webix.contrib.sender"
    label = 'dwsender'
    verbose_name = _("Django Webix Sender")

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.CONF = None

    def ready(self):
        self.CONF = getattr(settings, "WEBIX_SENDER", None)
        if self.CONF is None:
            raise ImproperlyConfigured(_('`WEBIX_SENDER` is not configured in your settings.py file'))

        self.send_methods_check()
        self.initial_send_methods_check()
        self.recipients_check()
        self.groups_can_send_check()
        self.extra_check()
        self.set_user_cost()

    def set_user_cost(self):
        from django_webix.contrib.sender.utils import my_import

        user_cost_config = getattr(self.CONF, "USER_COST", None)
        User = get_user_model()
        if user_cost_config is None:
            user_cost_config = 'django_webix.contrib.sender.send_methods.get_default_user_cost'
        _get_cost = my_import(user_cost_config)
        User.get_cost = _get_cost
        return _get_cost

    def send_methods_check(self):
        from django_webix.contrib.sender.utils import my_import

        for send_method in self.CONF['send_methods']:
            # Check common keys
            if 'method' not in send_method:
                raise ImproperlyConfigured(_("`method` is not configured in send method"))
            if 'verbose_name' not in send_method:
                raise ImproperlyConfigured(_("`verbose_name` is not configured in send method"))
            if 'show_in_list' not in send_method:
                raise ImproperlyConfigured(_("`show_in_list` is not configured in send method"))
            if 'show_in_chat' not in send_method:
                raise ImproperlyConfigured(_("`show_in_chat` is not configured in send method"))

            # Check functions or set defaults
            # Check function
            if 'function' not in send_method:
                if send_method['method'] == 'email':
                    send_method['function'] = 'django_webix.contrib.sender.send_methods.email.send'
                elif send_method['method'] == 'skebby':
                    send_method['function'] = 'django_webix.contrib.sender.send_methods.skebby.send'
                elif send_method['method'] == 'telegram':
                    send_method['function'] = 'django_webix.contrib.sender.send_methods.telegram.send'
                elif send_method['method'] == 'storage':
                    send_method['function'] = 'django_webix.contrib.sender.send_methods.storage.send'
                else:
                    raise ImproperlyConfigured(_("`function` is not configured in send method"))
            # Check recipients clean
            if 'recipients_clean' not in send_method:
                if send_method['method'] == 'email':
                    send_method['recipients_clean'] = 'django_webix.contrib.sender.send_methods.email.recipients_clean'
                elif send_method['method'] == 'skebby':
                    send_method['recipients_clean'] = 'django_webix.contrib.sender.send_methods.skebby.recipients_clean'
                elif send_method['method'] == 'telegram':
                    send_method['recipients_clean'] = 'django_webix.contrib.sender.send_methods.telegram.recipients_clean'
                elif send_method['method'] == 'storage':
                    send_method['recipients_clean'] = 'django_webix.contrib.sender.send_methods.storage.recipients_clean'
                else:
                    raise ImproperlyConfigured(_("`recipients_clean` is not configured in send method"))
            # Check presend check
            if 'presend_check' not in send_method:
                if send_method['method'] == 'email':
                    send_method['presend_check'] = 'django_webix.contrib.sender.send_methods.email.presend_check'
                elif send_method['method'] == 'skebby':
                    send_method['presend_check'] = 'django_webix.contrib.sender.send_methods.skebby.presend_check'
                elif send_method['method'] == 'telegram':
                    send_method['presend_check'] = 'django_webix.contrib.sender.send_methods.telegram.presend_check'
                elif send_method['method'] == 'storage':
                    send_method['presend_check'] = 'django_webix.contrib.sender.send_methods.storage.presend_check'
                else:
                    raise ImproperlyConfigured(_("`presend_check` is not configured in send method"))
            # Check attachments format
            if 'attachments_format' not in send_method:
                if send_method['method'] == 'email':
                    send_method['attachments_format'] = 'django_webix.contrib.sender.send_methods.email.attachments_format'
                elif send_method['method'] == 'skebby':
                    send_method['attachments_format'] = 'django_webix.contrib.sender.send_methods.skebby.attachments_format'
                elif send_method['method'] == 'telegram':
                    send_method['attachments_format'] = 'django_webix.contrib.sender.send_methods.telegram.attachments_format'
                elif send_method['method'] == 'storage':
                    send_method['attachments_format'] = 'django_webix.contrib.sender.send_methods.storage.attachments_format'
                else:
                    raise ImproperlyConfigured(_("`attachments_format` is not configured in send method"))

            # Try to import functions
            my_import(send_method['function'])
            my_import(send_method['recipients_clean'])
            my_import(send_method['presend_check'])
            my_import(send_method['attachments_format'])

            # Count method
            num = len([i for i in self.CONF['send_methods'] if i['method'] == send_method['method']])
            if num > 1:
                raise ImproperlyConfigured(
                    _('`{}` method is used {} times instead of 1'.format(send_method['method'], num))
                )

            # Init Email
            if send_method['method'] == 'email':
                # Check Email config
                if not 'config' in send_method or \
                    not 'from_email' in send_method['config']:
                    raise ImproperlyConfigured(_('Email `config` is not configured in your settings.py file'))

            # Init Skebby
            elif send_method['method'] == 'skebby':
                # Check Skebby config
                if not 'config' in send_method or \
                    not 'region' in send_method['config'] or \
                    not 'method' in send_method['config'] or \
                    not 'username' in send_method['config'] or \
                    not 'password' in send_method['config'] or \
                    not 'sender_string' in send_method['config']:
                    raise ImproperlyConfigured(_('Skebby `config` is not configured in your settings.py file'))

            # Init Telegram
            elif send_method['method'] == 'telegram':
                # Check Telegram config
                if not 'config' in send_method or \
                    not 'bot_token' in send_method['config']:
                    raise ImproperlyConfigured(_('Telegram `config` is not configured in your settings.py file'))
                # Update webhooks
                if 'webhooks' in send_method['config'] and \
                    isinstance(send_method['config']['webhooks'], list) and \
                    len(send_method['config']['webhooks']) > 0:
                    webhooks = send_method['config']['webhooks']
                    if not isinstance(webhooks, list):
                        webhooks = [webhooks]
                    try:
                        bot = telegram.Bot(token=send_method['config']['bot_token'])
                        # Remove old webhooks
                        bot.deleteWebhook()
                        # Add new webhooks
                        for webhook in webhooks:
                            bot.setWebhook(webhook)
                    except:
                        pass
                # Update commands
                if 'commands' in send_method['config'] and \
                    isinstance(send_method['config']['commands'], list) and \
                    len(send_method['config']['commands']) > 0:
                    try:
                        bot = telegram.Bot(token=send_method['config']['bot_token'])
                        bot.set_my_commands(send_method['config']['commands'])
                    except:
                        pass

            # Init storage
            elif send_method['method'] == 'storage':
                pass  # Nothing to check

    def initial_send_methods_check(self):
        from django_webix.contrib.sender.utils import my_import

        # Check initial_send_methods
        for initial_send_method in self.CONF['initial_send_methods']:
            # Check common keys
            if 'method' not in initial_send_method:
                raise ImproperlyConfigured(_("`method` is not configured in initial send method"))

            # Check function
            if 'function' not in initial_send_method:
                if initial_send_method['method'] == 'email':
                    initial_send_method['function'] = 'django_webix.contrib.sender.send_methods.email.send'
                elif initial_send_method['method'] == 'skebby':
                    initial_send_method['function'] = 'django_webix.contrib.sender.send_methods.skebby.send'
                elif initial_send_method['method'] == 'telegram':
                    initial_send_method['function'] = 'django_webix.contrib.sender.send_methods.telegram.send'
                elif initial_send_method['method'] == 'storage':
                    initial_send_method['function'] = 'django_webix.contrib.sender.send_methods.storage.send'
                else:
                    raise ImproperlyConfigured(_("`function` is not configured in send method"))

            # Try to import functions
            my_import(initial_send_method['function'])

    def recipients_check(self):
        if 'recipients' not in self.CONF:
            raise ImproperlyConfigured(_('`recipients` is not configured in your settings'))
        if not isinstance(self.CONF['recipients'], list):
            raise ImproperlyConfigured(_('`recipients` must be a list'))
        # Check recipients models
        for recipient in self.CONF['recipients']:
            if 'model' not in recipient or not isinstance(recipient['model'], str):
                raise ImproperlyConfigured(_('You have to define a `model` as string in your recipients list'))
            if 'datatable_fields' not in recipient or not isinstance(recipient['datatable_fields'], list):
                raise ImproperlyConfigured(_('You have to define a `datatable_fields` as list in your recipients list'))

            app_label, model = recipient['model'].lower().split(".")
            try:
                model = apps.get_model(app_label=app_label, model_name=model)
            except Exception:
                raise NotImplementedError(_('Recipient model `{}` is not valid'.format(recipient['model'])))

    def groups_can_send_check(self):
        if 'groups_can_send' in self.CONF and not isinstance(self.CONF['groups_can_send'], list):
            raise ImproperlyConfigured('`groups_can_send` value must be a list')

    def extra_check(self):
        if 'extra' in self.CONF and not isinstance(self.CONF['extra'], dict):
            raise NotADirectoryError('`extra` value must be a dict')
