# Generated by Django 2.2.28 on 2022-05-22 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200704_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_visible',
            field=models.BooleanField(default=True),
        ),
    ]
