# Generated by Django 4.2.6 on 2023-12-01 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userside', '0002_servicebooking'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicebooking',
            name='heavy_model_year',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='servicebooking',
            name='light_model_year',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='servicebooking',
            name='heavy_fuel_type',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='servicebooking',
            name='heavy_manufacturer',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='servicebooking',
            name='heavy_model_name',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='servicebooking',
            name='light_fuel_type',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='servicebooking',
            name='light_manufacturer',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='servicebooking',
            name='light_model_name',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='servicebooking',
            name='mini_fuel_type',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='servicebooking',
            name='mini_manufacturer',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='servicebooking',
            name='mini_model_name',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='servicebooking',
            name='mini_model_year',
            field=models.CharField(blank=True, choices=[], max_length=100, null=True),
        ),
    ]