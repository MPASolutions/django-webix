# Generated by Django 3.0.7 on 2020-08-10 09:50

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebixAdminMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nome nodo')),
                ('url', models.CharField(blank=True, max_length=1023, null=True, verbose_name='Web link')),
                ('enabled', models.BooleanField(blank=True, default=True, verbose_name='Abilitato')),
                ('active_all', models.BooleanField(blank=True, default=True, verbose_name='Attivo per tutti')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('groups', models.ManyToManyField(blank=True, to='auth.Group', verbose_name='Gruppi per i quali è abilitato')),
                ('model', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Modello')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='admin_webix.WebixAdminMenu')),
            ],
            options={
                'verbose_name': 'Menu',
                'verbose_name_plural': 'Menu',
            },
        ),
    ]
