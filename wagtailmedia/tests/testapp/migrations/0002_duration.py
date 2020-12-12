# Generated by Django 3.1.4 on 2020-12-12 03:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailmedia_tests', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custommedia',
            name='duration',
            field=models.FloatField(blank=True, default=0, help_text='Duration in seconds', validators=[django.core.validators.MinValueValidator(0)], verbose_name='duration'),
        ),
    ]
