# Generated by Django 3.2 on 2022-04-27 15:55

import django
from django.db import migrations

from django.db.models import JSONField


class Migration(migrations.Migration):

    dependencies = [
        ('django_webix_sender', '0007_auto_20210120_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagerecipient',
            name='extra_json',
            field=JSONField(blank=True, null=True, verbose_name='Extra JSON'),
        ),
    ]
