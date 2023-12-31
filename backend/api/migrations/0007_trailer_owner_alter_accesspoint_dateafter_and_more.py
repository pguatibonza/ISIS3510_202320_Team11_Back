# Generated by Django 4.2.5 on 2023-09-26 03:18

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0006_alter_accesspoint_dateafter_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="trailer",
            name="owner",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="TrailerOwner",
                to="api.user",
            ),
        ),
        migrations.AlterField(
            model_name="accesspoint",
            name="dateAfter",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 25, 22, 18, 24, 56823)
            ),
        ),
        migrations.AlterField(
            model_name="accesspoint",
            name="dateBefore",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 9, 25, 22, 18, 24, 56823)
            ),
        ),
        migrations.AlterField(
            model_name="trailer",
            name="driver",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="TrailerAssigned",
                to="api.user",
            ),
        ),
    ]
