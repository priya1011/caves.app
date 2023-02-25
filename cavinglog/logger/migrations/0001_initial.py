# Generated by Django 4.1.7 on 2023-02-25 22:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CavingTrip",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cave_name", models.CharField(max_length=100)),
                ("cave_region", models.CharField(max_length=100)),
                ("cave_country", models.CharField(max_length=100)),
                ("trip_start", models.DateTimeField()),
                ("trip_end", models.DateTimeField(blank=True)),
                ("trip_type", models.CharField(max_length=15)),
                ("trip_added", models.DateTimeField(auto_now_add=True)),
                ("trip_updated", models.DateTimeField(auto_now=True)),
                ("cavers", models.TextField(blank=True)),
                ("club", models.CharField(blank=True, max_length=100)),
                ("expedition", models.CharField(blank=True, max_length=100)),
                ("horizontal_distance", models.IntegerField(blank=True)),
                ("vertical_distance_down", models.IntegerField(blank=True)),
                ("vertical_distance_up", models.IntegerField(blank=True)),
                ("surveyed_distance", models.IntegerField(blank=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
