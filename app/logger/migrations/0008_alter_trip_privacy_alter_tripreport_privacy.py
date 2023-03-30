# Generated by Django 4.1.7 on 2023-03-30 03:45

from django.db import migrations, models


def change_tripreport_privacy(apps, schema_editor):
    TripReport = apps.get_model("logger", "TripReport")
    TripReport.objects.filter(privacy="Anyone, if they can view the trip").update(
        privacy="Default"
    )
    TripReport.objects.filter(privacy="Anyone, even if the trip is private").update(
        privacy="Public"
    )
    TripReport.objects.filter(privacy="Only my friends").update(privacy="Friends")
    TripReport.objects.filter(privacy="Only me").update(privacy="Private")


class Migration(migrations.Migration):
    dependencies = [
        ("logger", "0007_alter_trip_cavers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trip",
            name="privacy",
            field=models.CharField(
                choices=[
                    ("Default", "Anyone who can view my profile"),
                    ("Public", "Anyone, even if my profile is private"),
                    ("Friends", "Only my friends"),
                    ("Private", "Only me"),
                ],
                default="Default",
                max_length=10,
                verbose_name="Who can view this trip?",
            ),
        ),
        migrations.AlterField(
            model_name="tripreport",
            name="privacy",
            field=models.CharField(
                default="Default", max_length=40, verbose_name="Who can view this trip?"
            ),
        ),
        migrations.RunPython(change_tripreport_privacy),
        migrations.AlterField(
            model_name="tripreport",
            name="privacy",
            field=models.CharField(
                choices=[
                    ("Default", "Anyone who can view the trip"),
                    ("Public", "Anyone, even if the trip is private"),
                    ("Friends", "Only my friends"),
                    ("Private", "Only me"),
                ],
                default="Default",
                max_length=10,
                verbose_name="Who can view this report?",
            ),
        ),
    ]
