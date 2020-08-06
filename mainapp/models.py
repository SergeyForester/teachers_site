from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver

from apiapp.models import TeacherTimetableBooking


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	bio = models.TextField(max_length=500, blank=True)
	location = models.CharField(max_length=100, blank=True)
	rating = models.DecimalField(decimal_places=1, max_digits=3, max_length=30, default=0.0, null=True, blank=True)
	birth_date = models.DateField(null=True, blank=True)
	is_teacher = models.BooleanField(default=False)
	avatar = models.FileField(upload_to='avatars', default='avatars/default.png')
	video = models.FileField(upload_to='videos', null=True, blank=True)
	starting_price = models.DecimalField(decimal_places=2, max_digits=8, default=0.0, null=True, blank=True)
	work_day_start = models.CharField(max_length=5, default='08:00')
	work_day_end = models.CharField(max_length=5, default='20:00')

	def __str__(self):
		return self.user.first_name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()


class CourseType(models.Model):
	name = models.CharField(max_length=100)


class LessonType(models.Model):
	course_type = models.ForeignKey(CourseType, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)


class Lesson(models.Model):
	lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=7, decimal_places=2)
	minutes = models.PositiveIntegerField()
	is_group = models.BooleanField(default=False)
	places = models.IntegerField(default=1)


@receiver(post_save, sender=Lesson)
def set_starting_price(sender, instance, **kwargs):
	if instance.lesson_type.user.profile.starting_price > instance.price:
		instance.lesson_type.user.profile.starting_price = instance.price
		instance.lesson_type.user.profile.save()


class TeacherTimetable(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)


# class TeacherTimetableBooking(models.Model): was replaced to apiapp


class LessonBooking(models.Model):
	datetime = models.DateTimeField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
	timetable_booking = models.ForeignKey(TeacherTimetableBooking, null=True, blank=True, on_delete=models.CASCADE)
	is_completed = models.BooleanField(default=False)



