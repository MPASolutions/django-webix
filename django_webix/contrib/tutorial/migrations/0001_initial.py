# Generated by Django 3.2.16 on 2022-11-14 16:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TutorialArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Tutorial area',
                'verbose_name_plural': 'Tutorial areas',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TutorialItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('url', models.URLField(max_length=255, verbose_name='URL')),
                ('tutorial_type', models.CharField(choices=[('pdf', 'PDF'), ('video', 'Video')], max_length=32, verbose_name='Tutorial type')),
                ('target', models.CharField(choices=[('iframe', 'Modal with iframe'), ('_self', 'Same window'), ('_blank', 'New tab')], default='_self', max_length=32, verbose_name='Type of opening file')),
                ('visible_from', models.DateField(blank=True, null=True, verbose_name='Visible from')),
                ('visible_to', models.DateField(blank=True, null=True, verbose_name='Visible to')),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dwtutorial.tutorialarea', verbose_name='Area')),
            ],
            options={
                'verbose_name': 'Tutorial item',
                'verbose_name_plural': 'Tutorial items',
                'ordering': ['name'],
            },
        ),
    ]
