# Generated by Django 4.1.7 on 2023-04-20 14:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0018_copy_show_statistics"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="show_statistics",
        ),
    ]
