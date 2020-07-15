from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	bio = models.TextField(max_length=500, blank=True)
	location = models.CharField(max_length=30, blank=True)
	rating = models.DecimalField(decimal_places=1, max_digits=3, max_length=30, default=0.0, null=True, blank=True)
	birth_date = models.DateField(null=True, blank=True)
	is_teacher = models.BooleanField(default=False)

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


class TeacherTimetable(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)


class LessonBooking(models.Model):
	datetime = models.DateTimeField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)


class TeacherTimetableBooking(models.Model):
	lesson_booking = models.ForeignKey(LessonBooking, on_delete=models.CASCADE)
	timetable = models.ForeignKey(TeacherTimetable, on_delete=models.CASCADE)
