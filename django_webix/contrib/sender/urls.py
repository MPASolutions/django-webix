from django.conf import settings
from django.urls import path, re_path

from django_webix.contrib.sender.views import (SenderListView, SenderGetListView, SenderSendView, SenderWindowView,
                                               SenderInvoiceManagementView, SenderTelegramWebhookView,
                                               SenderMessagesListView, SenderMessagesChatView, CheckAttachmentView,
                                               GetMessageUnreadView)

CONF = getattr(settings, "WEBIX_SENDER", None)

urlpatterns = [
    path('message_unread', GetMessageUnreadView.as_view(), name="dwsender.message_unread"),
    path('list', SenderListView.as_view(), name="dwsender.list"),
    path('getlist', SenderGetListView.as_view(), name="dwsender.getlist"),
    path('send', SenderSendView.as_view(), name="dwsender.send"),
    path('sender-window', SenderWindowView.as_view(), name='dwsender.sender_window'),
    path('invoices', SenderInvoiceManagementView.as_view(), name='dwsender.invoices'),
    path('messages_list', SenderMessagesListView.as_view(), name='dwsender.messages_list'),
    path('attachment_check', CheckAttachmentView.as_view(), name='dwsender.attachment_check'),
    re_path('^messages_chat/(?P<section>users|messages)$', SenderMessagesChatView.as_view(),
            name='dwsender.messages_chat'),

    path('messages_list/typology/<int:typology_pk>', SenderMessagesListView.as_view(),
         name='dwsender.messages_list.typology'),
    path('messages_list/typologiesgroup/<int:typologiesgroup_pk>', SenderMessagesListView.as_view(),
         name='dwsender.messages_list.typologiesgroup'),

]

#if CONF is not None and CONF['typology_model']['enabled']:
#    urlpatterns.append(
#        path('messages_list/typology/<str:title>/<str:pk>', SenderMessagesListView.as_view(),
#             name='dwsender.messages_list.typology'),
#    )

# Telegram
if CONF is not None and any(_send_method['method'] == 'telegram' for _send_method in CONF.get('send_methods', [])):
    urlpatterns.append(
        path('telegram/webhook/', SenderTelegramWebhookView.as_view()),
    )
