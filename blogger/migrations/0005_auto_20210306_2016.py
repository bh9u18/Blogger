# Generated by Django 3.1.7 on 2021-03-06 14:46

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blogger', '0004_auto_20210222_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 6, 14, 46, 46, 783835, tzinfo=utc)),
        ),
    ]
