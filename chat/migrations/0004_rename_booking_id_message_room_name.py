# Generated by Django 4.2.6 on 2024-01-15 12:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_alter_message_options_remove_message_content_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='booking_id',
            new_name='room_name',
        ),
    ]
