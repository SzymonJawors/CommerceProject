# Generated by Django 5.1.3 on 2025-01-07 20:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_watchlist'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='watchlist',
            unique_together={('user', 'auction')},
        ),
    ]
