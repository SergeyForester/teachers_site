# Generated by Django 3.0.7 on 2020-08-06 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apiapp', '0003_auto_20200805_1615'),
        ('mainapp', '0004_auto_20200805_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessonbooking',
            name='timetable_booking',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apiapp.TeacherTimetableBooking'),
        ),
    ]
