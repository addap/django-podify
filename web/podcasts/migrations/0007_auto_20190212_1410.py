# Generated by Django 2.1.5 on 2019-02-12 14:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0006_auto_20190212_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
    ]