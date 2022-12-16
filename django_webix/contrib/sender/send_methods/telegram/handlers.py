
import phonenumbers
from django.apps import apps
from django.conf import settings
from django.utils.translation import gettext as _
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import CallbackContext, DispatcherHandlerStop, ConversationHandler, CommandHandler, MessageHandler, \
    Filters


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text(_('Hi!'))


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(_('Help!'))


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def check_user(update: Update, context: CallbackContext) -> None:
    """Check if user is enabled to chat with bot"""

    CONF = getattr(settings, "WEBIX_SENDER", None)

    # Check in every enabled models
    _exists = False
    for recipient in CONF['recipients']:
        app_label, model = recipient['model'].lower().split(".")
        model_class = apps.get_model(app_label=app_label, model_name=model)
        if model_class.get_telegram_fieldpath():
            _exists = model_class.objects.filter(
                **{model_class.get_telegram_fieldpath(): update.message.from_user.id}
            ).exists()
            if _exists:
                break

    if not _exists:
        update.message.reply_text(_("Your user is not authorized to use this Bot"))
        raise DispatcherHandlerStop()


def start_phone_number(update: Update, context: CallbackContext) -> int:
    """Initial command that requires phone number to register user"""

    update.message.reply_text(
        _('Hi! Send me your phone number to connect your web account!\nType /cancel to exit'),
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(text=_("Send my phone number"), request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return 0


def check_phone_number(update: Update, context: CallbackContext) -> int:
    """Check if user's phone number is in recipients records"""

    CONF = getattr(settings, "WEBIX_SENDER", None)

    number = phonenumbers.parse("+{}".format(update.message.contact.phone_number))

    # Check recipients
    _found = False
    for recipient in CONF['recipients']:
        app_label, model = recipient['model'].lower().split(".")
        model_class = apps.get_model(app_label=app_label, model_name=model)
        if model_class.get_telegram_fieldpath():
            _recipients = model_class.objects.filter(**{
                "{}__endswith".format(model_class.get_sms_fieldpath()): number.national_number
            })
            _exists = _recipients.exists()
            if not _found:
                _found = _exists
            if _exists:
                _recipients.update(**{model_class.get_telegram_fieldpath(): update.message.from_user.id})
                update.message.reply_text(
                    _('Welcome {}! Now you can use this bot').format(_recipients.first()),
                    reply_markup=ReplyKeyboardRemove()
                )
    if not _found:
        update.message.reply_text(
            _('Your number is not in our database, contact us to add'),
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


def cancel_phone_number(update: Update, context: CallbackContext) -> int:
    """Cancel phone number registration procedure"""

    update.message.reply_text(
        _("Okay, if you want to connect your account type /start"),
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


phone_number_handler = ConversationHandler(
    allow_reentry=True,
    entry_points=[CommandHandler('start', start_phone_number)],
    states={
        0: [MessageHandler(Filters.contact, check_phone_number)],
    },
    fallbacks=[CommandHandler('cancel', cancel_phone_number)],
    persistent=True,
    name="phone_number"
)
