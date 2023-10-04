# Generated by Django 4.2.5 on 2023-09-26 18:02

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0009_alter_accesspoint_dateafter_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accesspoint",
            name="dateAfter",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 26, 13, 2, 54, 540074)
            ),
        ),
        migrations.AlterField(
            model_name="accesspoint",
            name="dateBefore",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 26, 13, 2, 54, 540074)
            ),
        ),
        migrations.AlterField(
            model_name="trip",
            name="dropoff",
            field=models.OneToOneField(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="dropoff",
                to="api.accesspoint",
            ),
        ),
    ]
