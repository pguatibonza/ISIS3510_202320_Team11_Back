# Generated by Django 4.2.5 on 2023-09-27 00:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0010_alter_accesspoint_dateafter_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accesspoint",
            name="dateAfter",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 26, 19, 19, 1, 93425)
            ),
        ),
        migrations.AlterField(
            model_name="accesspoint",
            name="dateBefore",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 26, 19, 19, 1, 93425)
            ),
        ),
    ]
