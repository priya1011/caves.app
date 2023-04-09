# Generated by Django 4.1.7 on 2023-04-09 16:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0008_alter_cavinguser_privacy"),
    ]

    operations = [
        migrations.AddField(
            model_name="cavinguser",
            name="last_seen",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
