# Generated by Django 3.1.5 on 2021-06-18 10:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20210618_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='watchlist',
            field=models.ManyToManyField(blank=True, related_name='watchlist', to=settings.AUTH_USER_MODEL),
        ),
    ]
