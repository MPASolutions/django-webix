# Generated by Django 3.2.16 on 2022-11-24 09:52

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
CONF = getattr(settings, "WEBIX_SENDER", None)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerTypology',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typology', models.CharField(max_length=255, unique=True, verbose_name='Typology')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Modification data')),
            ],
            options={
                'verbose_name': 'Customer typology',
                'verbose_name_plural': 'Customer typologies',
            },
        ),
        migrations.CreateModel(
            name='ExternalSubjectTypology',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typology', models.CharField(max_length=255, unique=True, verbose_name='Typology')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Modification data')),
            ],
            options={
                'verbose_name': 'External subject typology',
                'verbose_name_plural': 'External subject typologies',
            },
        ),
        migrations.CreateModel(
            name='MessageAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=CONF['attachments']['upload_folder'], verbose_name='Document')),
                ('insert_date', models.DateTimeField(auto_now_add=True, verbose_name='Insert date')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Modification data')),
            ],
            options={
                'verbose_name': 'Attachment',
                'verbose_name_plural': 'Attachments',
            },
        ),
        migrations.CreateModel(
            name='MessageTypology',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typology', models.CharField(max_length=255, unique=True, verbose_name='Typology')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Modification data')),
            ],
            options={
                'verbose_name': 'Message typology',
                'verbose_name_plural': 'Message typologies',
            },
        ),
        migrations.CreateModel(
            name='TelegramPersistence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typology', models.CharField(choices=[('user_data', 'user_data'), ('chat_data', 'chat_data'), ('bot_data', 'bot_data'), ('conversations', 'conversations')], max_length=32, unique=True)),
                ('data', models.JSONField()),
            ],
            options={
                'verbose_name': 'Telegram Persistence',
                'verbose_name_plural': 'Telegram Persistences',
            },
        ),
        migrations.CreateModel(
            name='MessageSent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_method', models.CharField(max_length=255, verbose_name='Send method')),
                ('subject', models.TextField(blank=True, null=True, verbose_name='Subject')),
                ('body', models.TextField(blank=True, null=True, verbose_name='Body')),
                ('status', models.CharField(choices=[('sent', 'Sent'), ('received', 'Received')], default='sent', max_length=16)),
                ('extra', models.JSONField(blank=True, null=True, verbose_name='Extra')),
                ('cost', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=6, verbose_name='Cost')),
                ('invoiced', models.BooleanField(default=False, verbose_name='Invoiced')),
                ('sender', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sender')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Modification data')),
                ('attachments', models.ManyToManyField(blank=True, db_constraint=False, to=CONF['attachments']['model'], verbose_name='Attachments')),
                ('typology', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dwsender.messagetypology', verbose_name='Typology')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Sent message',
                'verbose_name_plural': 'Sent messages',
            },
        ),
        migrations.CreateModel(
            name='MessageRecipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('recipient_address', models.CharField(max_length=255, verbose_name='Recipient address')),
                ('sent_number', models.IntegerField(default=1, verbose_name='Sent number')),
                ('status', models.CharField(choices=[('success', 'Success'), ('failed', 'Failed'), ('unknown', 'Unknown'), ('invalid', 'Invalid'), ('duplicate', 'Duplicate')], default='unknown', max_length=32)),
                ('extra', models.TextField(blank=True, null=True, verbose_name='Extra')),
                ('extra_json', models.JSONField(blank=True, null=True, verbose_name='Extra JSON')),
                ('is_sender', models.BooleanField(blank=True, default=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Modification data')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('message_sent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dwsender.messagesent', verbose_name='Message sent')),
            ],
            options={
                'verbose_name': 'Recipient',
                'verbose_name_plural': 'Recipients',
            },
        ),
        migrations.CreateModel(
            name='ExternalSubject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('vat_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Vat number')),
                ('fiscal_code', models.CharField(blank=True, max_length=32, null=True, verbose_name='Fiscal code')),
                ('sms', models.CharField(blank=True, max_length=32, null=True, verbose_name='Sms')),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='Email')),
                ('telegram', models.CharField(blank=True, max_length=255, null=True, verbose_name='Telegram')),
                ('note', models.TextField(blank=True, null=True, verbose_name='Note')),
                ('extra', models.JSONField(blank=True, null=True, verbose_name='Extra')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Modification data')),
                ('typology', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dwsender.externalsubjecttypology', verbose_name='Typology')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'External subject',
                'verbose_name_plural': 'External subjects',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('vat_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Vat number')),
                ('fiscal_code', models.CharField(blank=True, max_length=32, null=True, verbose_name='Fiscal code')),
                ('sms', models.CharField(blank=True, max_length=32, null=True, verbose_name='Sms')),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='Email')),
                ('telegram', models.CharField(blank=True, max_length=255, null=True, verbose_name='Telegram')),
                ('note', models.TextField(blank=True, null=True, verbose_name='Note')),
                ('extra', models.JSONField(blank=True, null=True, verbose_name='Extra')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Modification data')),
                ('typology', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dwsender.customertypology', verbose_name='Typology')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
            },
        ),
        migrations.CreateModel(
            name='MessageUserRead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Modification data')),
                ('message_sent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dwsender.messagesent', verbose_name='Message sent')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Readed message',
                'verbose_name_plural': 'Readed messages',
                'unique_together': {('message_sent', 'user')},
            },
        ),
    ]
