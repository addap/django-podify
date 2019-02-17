# Generated by Django 2.1.5 on 2019-02-15 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0019_podcast_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='episode',
            name='pub_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
