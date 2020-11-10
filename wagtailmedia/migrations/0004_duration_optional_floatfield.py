# Generated by Django 2.2.8 on 2020-08-17 15:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailmedia", "0003_copy_media_permissions_to_collections"),
    ]

    operations = [
        migrations.AlterField(
            model_name="media",
            name="duration",
            field=models.FloatField(
                blank=True,
                default=0,
                help_text="Duration in seconds",
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="duration",
            ),
        ),
    ]
