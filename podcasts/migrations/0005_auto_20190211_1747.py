# Generated by Django 2.1.5 on 2019-02-11 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0004_auto_20190211_1736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='mp3',
            field=models.FileField(upload_to=None),
        ),
    ]
