# Generated by Django 2.1.5 on 2019-02-12 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0009_auto_20190212_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='downloaded',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
