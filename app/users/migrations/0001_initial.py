# Generated by Django 4.1.7 on 2023-03-13 04:32

from django.db import migrations, models
import django_countries.fields
import timezone_field.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CavingUser",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="This will be verified before you can log in.",
                        max_length=255,
                        unique=True,
                        verbose_name="email address",
                    ),
                ),
                (
                    "username",
                    models.SlugField(
                        help_text="A unique identifier that will be part of the web address for your logbook.",
                        max_length=30,
                        unique=True,
                    ),
                ),
                ("first_name", models.CharField(max_length=30)),
                ("last_name", models.CharField(max_length=30)),
                ("location", models.CharField(blank=True, max_length=50)),
                (
                    "country",
                    django_countries.fields.CountryField(blank=True, max_length=2),
                ),
                ("bio", models.TextField(blank=True, verbose_name="about me")),
                ("club", models.CharField(blank=True, max_length=50)),
                (
                    "timezone",
                    timezone_field.fields.TimeZoneField(
                        choices_display="WITH_GMT_OFFSET", default="Europe/London"
                    ),
                ),
                (
                    "units",
                    models.CharField(
                        choices=[("Metric", "Metric"), ("Imperial", "Imperial")],
                        default="Metric",
                        max_length=10,
                        verbose_name="Distance units",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=False,
                        help_text="Only enabled users are able to sign in. Users are disabled until their email is verified.",
                        verbose_name="Enabled user",
                    ),
                ),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
            },
        ),
    ]
