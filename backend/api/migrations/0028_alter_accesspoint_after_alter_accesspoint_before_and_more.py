# Generated by Django 4.2.5 on 2023-10-03 13:32

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_alter_accesspoint_after_alter_accesspoint_before'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesspoint',
            name='after',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 3, 13, 32, 47, 73107)),
        ),
        migrations.AlterField(
            model_name='accesspoint',
            name='before',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 3, 13, 32, 47, 73097)),
        ),
        migrations.AlterField(
            model_name='trip',
            name='trailer',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.trailer'),
        ),
    ]
