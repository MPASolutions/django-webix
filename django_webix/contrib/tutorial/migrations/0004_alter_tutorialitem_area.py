from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_webix_tutorial', '0003_auto_20210527_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialitem',
            name='area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_webix_tutorial.tutorialarea', verbose_name='Area'),
        ),
    ]
