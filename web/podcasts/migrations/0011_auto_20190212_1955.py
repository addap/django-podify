# Generated by Django 2.1.5 on 2019-02-12 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0010_auto_20190212_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='downloaded',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='episode',
            name='mp3',
            field=models.FileField(blank=True, upload_to=None),
        ),
    ]