# Generated by Django 2.1.5 on 2019-02-11 00:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0002_auto_20190204_1832'),
    ]

    operations = [
        migrations.RenameField(
            model_name='podcast',
            old_name='title',
            new_name='slug',
        ),
    ]
