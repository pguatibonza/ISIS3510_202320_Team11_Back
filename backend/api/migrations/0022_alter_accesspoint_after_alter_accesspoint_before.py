# Generated by Django 4.2.5 on 2023-09-28 00:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0021_alter_accesspoint_after_alter_accesspoint_before"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accesspoint",
            name="after",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 27, 19, 52, 38, 407783)
            ),
        ),
        migrations.AlterField(
            model_name="accesspoint",
            name="before",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 27, 19, 52, 38, 407783)
            ),
        ),
    ]