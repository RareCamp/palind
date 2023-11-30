# Generated by Django 4.2.3 on 2023-11-28 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0007_remove_submission_gender_token_and_more"),
        (
            "accounts",
            "0008_rename_prevalence_counting_user_customuser_is_prevalence_counting_user",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="default_dataset",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="datasets.dataset",
            ),
        ),
    ]