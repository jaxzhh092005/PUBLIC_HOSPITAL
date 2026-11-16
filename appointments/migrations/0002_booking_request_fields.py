import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def fail_if_legacy_appointments_exist(apps, schema_editor):
    Appointment = apps.get_model("appointments", "Appointment")
    if Appointment.objects.using(schema_editor.connection.alias).exists():
        raise RuntimeError(
            "Legacy appointments exist. Export or map their patient, doctor, and reason "
            "data before applying this schema migration."
        )


class Migration(migrations.Migration):

    dependencies = [
        ("appointments", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(fail_if_legacy_appointments_exist, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name="appointment",
            options={"ordering": ["-created_at"]},
        ),
        migrations.RemoveField(
            model_name="appointment",
            name="doctor",
        ),
        migrations.RemoveField(
            model_name="appointment",
            name="patient",
        ),
        migrations.RemoveField(
            model_name="appointment",
            name="reason",
        ),
        migrations.AddField(
            model_name="appointment",
            name="barangay",
            field=models.CharField(default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="birthdate",
            field=models.DateField(default=datetime.date(1970, 1, 1)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="contact_number",
            field=models.CharField(default="", max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="doctor_name",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="appointment",
            name="doctor_photo",
            field=models.ImageField(blank=True, upload_to="doctor_photos/"),
        ),
        migrations.AddField(
            model_name="appointment",
            name="email",
            field=models.EmailField(default="", max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="first_name",
            field=models.CharField(default="", max_length=60),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="gender",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="hospital_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="appointment",
            name="last_name",
            field=models.CharField(default="", max_length=60),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="middle_name",
            field=models.CharField(blank=True, max_length=60),
        ),
        migrations.AddField(
            model_name="appointment",
            name="municipality",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="province",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="region",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="specialization",
            field=models.CharField(default="", max_length=60),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="street",
            field=models.CharField(default="", max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="appointment",
            name="suffix",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name="appointment",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="appointments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="appointment",
            name="valid_id",
            field=models.FileField(default="", upload_to="appointment_ids/"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="appointment",
            name="appointment_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("confirmed", "Confirmed"),
                    ("cancelled", "Cancelled"),
                ],
                default="pending",
                max_length=12,
            ),
        ),
    ]
