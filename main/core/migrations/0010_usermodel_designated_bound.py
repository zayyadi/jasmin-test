# Generated by Django 4.2.9 on 2024-03-12 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_usermodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermodel',
            name='designated_bound',
            field=models.IntegerField(default=0),
        ),
    ]
