# Generated by Django 4.1.2 on 2022-11-18 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("intecomm_rando", "0002_historicalrandomizationlist_randomizationlist"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalregisteredgroup",
            name="randomization_datetime",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="registeredgroup",
            name="randomization_datetime",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="historicalregisteredgroup",
            name="group_identifier",
            field=models.CharField(db_index=True, max_length=36),
        ),
        migrations.AlterField(
            model_name="historicalregisteredgroup",
            name="group_identifier_as_pk",
            field=models.UUIDField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalregisteredgroup",
            name="registration_datetime",
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name="registeredgroup",
            name="group_identifier",
            field=models.CharField(max_length=36, unique=True),
        ),
        migrations.AlterField(
            model_name="registeredgroup",
            name="group_identifier_as_pk",
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name="registeredgroup",
            name="registration_datetime",
            field=models.DateTimeField(),
        ),
    ]
