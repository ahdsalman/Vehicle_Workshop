# Generated by Django 4.2.6 on 2023-10-30 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0003_alter_user_first_name_alter_user_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_shopowner',
            field=models.BooleanField(default=False),
        ),
    ]