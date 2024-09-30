# Generated by Django 4.2.7 on 2023-11-11 18:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_control', '0002_alter_customuser_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'admin'), ('user_1', 'user'), ('user_2', 'user'), ('user_3', 'user')], max_length=8),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='token',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tokenwpp_relations', to='user_control.tokenwpp'),
        ),
    ]
