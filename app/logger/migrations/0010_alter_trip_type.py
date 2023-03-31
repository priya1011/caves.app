# Generated by Django 4.1.7 on 2023-03-31 19:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logger", "0009_trip_resurveyed_dist_trip_resurveyed_dist_units_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trip",
            name="type",
            field=models.CharField(
                choices=[
                    ("Sport", "Sport"),
                    ("Digging", "Digging"),
                    ("Survey", "Survey"),
                    ("Exploration", "Exploration"),
                    ("Aid climbing", "Aid climbing"),
                    ("Photography", "Photography"),
                    ("Training", "Training"),
                    ("Rescue", "Rescue"),
                    ("Science", "Science"),
                    ("Hauling", "Hauling"),
                    ("Rigging", "Rigging"),
                    ("Surface", "Surface"),
                    ("Other", "Other"),
                ],
                default="Sport",
                max_length=15,
            ),
        ),
    ]
