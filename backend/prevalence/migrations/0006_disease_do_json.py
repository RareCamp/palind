# Generated by Django 4.2.3 on 2023-12-28 10:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("prevalence", "0005_remove_disease_icd10_id_remove_disease_omim_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="disease",
            name="do_json",
            field=models.JSONField(blank=True, null=True),
        ),
    ]