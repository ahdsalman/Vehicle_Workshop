# Generated by Django 4.2.6 on 2024-01-02 14:00

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=100)),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Workshopdetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shopname', models.CharField(max_length=255, null=True)),
                ('phone', models.CharField(max_length=13, null=True, unique=True)),
                ('branch', models.CharField(blank=True, max_length=100, null=True)),
                ('id_proof', models.FileField(blank=True, null=True, upload_to='id_proof')),
                ('is_approved', models.BooleanField(blank=True, default=False, null=True)),
                ('is_oppen', models.BooleanField(blank=True, default=True, null=True)),
                ('shop_coordinates', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('district', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('place', models.CharField(blank=True, max_length=100, null=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shopdetails.category')),
                ('services', models.ManyToManyField(blank=True, related_name='services', to='shopdetails.services')),
                ('shop_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workshops', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
