# Generated by Django 2.0 on 2019-01-01 09:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_auto_20190101_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='expired_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 31, 17, 51, 53, 446832)),
        ),
    ]
