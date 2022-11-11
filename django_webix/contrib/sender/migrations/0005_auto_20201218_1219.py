# Generated by Django 2.2.9 on 2020-12-18 12:19

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


def update_send_method(apps, schema_editor):
    try:
        model = apps.get_model('django_webix_sender', 'MessageSent')
    except Exception:
        return

    model.objects.filter(
        send_method='sms.django_webix_sender.send_methods.skebby.send_sms'
    ).update(
        send_method='skebby.django_webix_sender.send_methods.skebby.send'
    )
    model.objects.filter(
        send_method='email.django_webix_sender.send_methods.email.send_email'
    ).update(
        send_method='email.django_webix_sender.send_methods.email.send'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('django_webix_sender', '0004_auto_20201216_1040'),
    ]

    operations = [
        migrations.RunPython(update_send_method, hints={'model_name': 'messagesent'}),
        migrations.CreateModel(
            name='TelegramPersistence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typology', models.CharField(choices=[('user_data', 'user_data'), ('chat_data', 'chat_data'), ('bot_data', 'bot_data'), ('conversations', 'conversations')], max_length=32, unique=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={
                'verbose_name': 'Telegram Persistence',
                'verbose_name_plural': 'Telegram Persistences',
            },
        ),
    ]
