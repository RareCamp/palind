# Generated by Django 4.2.3 on 2023-12-29 16:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("prevalence", "0007_alter_patientsbysource_source"),
        ("datasets", "0013_remove_submission_abbr_zip_code_at_birth_token"),
    ]

    operations = [
        migrations.AlterField(
            model_name="submission",
            name="disease",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="prevalence.disease"
            ),
        ),
    ]