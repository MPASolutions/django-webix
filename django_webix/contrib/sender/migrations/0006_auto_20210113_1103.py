# Generated by Django 3.1.5 on 2021-01-13 11:03

import django
from django.conf import settings
from django.db import migrations, models

from django.db.models import JSONField

CONF = getattr(settings, "WEBIX_SENDER", None)


class Migration(migrations.Migration):
    dependencies = [
        ('django_webix_sender', '0005_auto_20201218_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagesent',
            name='status',
            field=models.CharField(choices=[('sent', 'Sent'), ('received', 'Received')], default='sent', max_length=16),
        ),
        migrations.AlterField(
            model_name='telegrampersistence',
            name='data',
            field=JSONField(),
        ),
        migrations.AddField(
            model_name='messagerecipient',
            name='read',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='messagerecipient',
            name='is_sender',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]

    if any(_recipients['model'] == 'django_webix_sender.Customer' for _recipients in CONF['recipients']):
        operations.append(migrations.AlterField(
            model_name='customer',
            name='extra',
            field=JSONField(blank=True, null=True, verbose_name='Extra'),
        ))
    if any(_recipients['model'] == 'django_webix_sender.ExternalSubject' for _recipients in CONF['recipients']):
        operations.append(migrations.AlterField(
            model_name='externalsubject',
            name='extra',
            field=JSONField(blank=True, null=True, verbose_name='Extra'),
        ))
