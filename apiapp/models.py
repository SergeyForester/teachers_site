from django.db import models

# Create your models here.


class TeacherTimetableBooking(models.Model):
	PENDING = 'pending'
	BOOKED = 'booked'
	STATUS = (
		(PENDING, PENDING),
		(BOOKED, BOOKED),
	)


	timetable = models.ForeignKey(to="mainapp.TeacherTimetable", on_delete=models.CASCADE)
	lesson_booking = models.ForeignKey(to="mainapp.LessonBooking", on_delete=models.CASCADE)
	status = models.CharField(choices=STATUS, max_length=9, default=PENDING)