# Generated by Django 2.1.5 on 2019-02-21 10:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0025_auto_20190221_0113'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='episode',
            name='playlist_episode',
        ),
    ]