# Generated by Django 3.1.2 on 2020-10-19 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson_confirmation_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacherbill',
            name='is_payed',
            field=models.BooleanField(default=False),
        ),
    ]
