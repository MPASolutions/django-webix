# Generated by Django 3.2.16 on 2022-11-14 16:29

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ImportFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('allegato', models.FileField(blank=True, null=True, upload_to='import_file', verbose_name='Attachment')),
            ],
        ),
    ]
