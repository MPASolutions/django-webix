# Generated by Django 3.1.5 on 2021-01-20 04:06

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('admin_webix', '0003_webixadminmenu_icon'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='webixadminmenu',
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
    ]
