# Generated by Django 4.2.7 on 2024-09-30 18:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_control', '0006_alter_customuser_token_group'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Group',
            new_name='WPPGroup',
        ),
    ]
