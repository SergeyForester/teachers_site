# Generated by Django 2.1.3 on 2020-07-30 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='work_day_end',
            field=models.CharField(default='20:00', max_length=4),
        ),
        migrations.AddField(
            model_name='profile',
            name='work_day_start',
            field=models.CharField(default='08:00', max_length=4),
        ),
    ]
