
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


@property
def _filters_messages(self):
    return Q(
        # Model django_webix_sender.Customer filter
        Q(customer_message_recipients__user=self) |
        # Model django_webix_sender.ExternalSubject
        Q(externalsubject_message_recipients__user=self)
    )


User.filters_messages = _filters_messages
