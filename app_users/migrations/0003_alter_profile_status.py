# Generated by Django 4.1.3 on 2023-01-10 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_users', '0002_alter_profile_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='status',
            field=models.CharField(choices=[('1', 'Beginner'), ('2', 'Advanced'), ('3', 'Expert')], default='1', max_length=1),
        ),
    ]
