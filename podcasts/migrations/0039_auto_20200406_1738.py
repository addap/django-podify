# Generated by Django 3.0.5 on 2020-04-06 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0038_auto_20200404_2357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='slug',
            field=models.SlugField(blank=True, max_length=100),
        ),
    ]
