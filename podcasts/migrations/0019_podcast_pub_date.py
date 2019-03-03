# Generated by Django 2.1.5 on 2019-02-15 21:10

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0018_remove_episode_downloaded'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcast',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
