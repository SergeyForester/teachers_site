# Generated by Django 3.0.7 on 2020-07-15 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_auto_20200715_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='starting_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.FileField(default='media/avatar/default.png', upload_to='avatars'),
        ),
    ]