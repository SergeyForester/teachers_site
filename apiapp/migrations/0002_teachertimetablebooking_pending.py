# Generated by Django 3.0.7 on 2020-08-05 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teachertimetablebooking',
            name='pending',
            field=models.BooleanField(default=False),
        ),
    ]