# Generated by Django 4.1.7 on 2023-03-13 04:32

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Trip",
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
                ("start", models.DateTimeField(verbose_name="start time")),
                (
                    "end",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="end time"
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("Sport", "Sport"),
                            ("Digging", "Digging"),
                            ("Survey", "Survey"),
                            ("Exploration", "Exploration"),
                            ("Aid climbing", "Aid climbing"),
                            ("Photography", "Photography"),
                            ("Training", "Training"),
                            ("Rescue", "Rescue"),
                        ],
                        default="Sport",
                        max_length=15,
                    ),
                ),
                (
                    "added",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="trip added on"
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="trip last updated"
                    ),
                ),
                ("cavers", models.CharField(blank=True, max_length=200)),
                ("club", models.CharField(blank=True, max_length=100)),
                ("expedition", models.CharField(blank=True, max_length=100)),
                (
                    "horizontal_dist",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="horizontal distance",
                    ),
                ),
                (
                    "vert_dist_down",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="rope descent distance",
                    ),
                ),
                (
                    "vert_dist_up",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="rope ascent distance",
                    ),
                ),
                (
                    "surveyed_dist",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="surveyed distance",
                    ),
                ),
                (
                    "aid_dist",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="aid climbing distance",
                    ),
                ),
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
