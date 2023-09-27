# Generated by Django 4.2.5 on 2023-09-27 00:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0014_alter_accesspoint_dateafter_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="accesspoint", name="dateAfter",),
        migrations.RemoveField(model_name="accesspoint", name="dateBefore",),
        migrations.AddField(
            model_name="accesspoint",
            name="after",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 26, 19, 50, 22, 293441)
            ),
        ),
        migrations.AddField(
            model_name="accesspoint",
            name="before",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 26, 19, 50, 22, 293441)
            ),
        ),
    ]