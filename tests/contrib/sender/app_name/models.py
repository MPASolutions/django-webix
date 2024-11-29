from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


@property
def _filters_messages(self):
    return Q(
        # Model dwsender.Customer filter
        Q(customer_message_recipients__user=self)
        |
        # Model dwsender.ExternalSubject
        Q(externalsubject_message_recipients__user=self)
    )


User.filters_messages = _filters_messages
