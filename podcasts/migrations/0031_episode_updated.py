# Generated by Django 3.0.5 on 2020-04-03 17:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('podcasts', '0030_auto_20190303_2332'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='updated',
            field=models.BooleanField(default=False),
        ),
    ]
