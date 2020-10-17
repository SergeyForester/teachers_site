import datetime

from mainapp.models import LessonBooking
from teachers import settings


def cost_of_using(user_id=None):
	cost = 0

	if user_id:
		bookings = LessonBooking.objects.filter(lesson__lesson_type__user__id=user_id,
		                                        datetime__month=datetime.datetime.now().month)
	else:
		bookings = LessonBooking.objects.filter(datetime__month=datetime.datetime.today().month)

	for booking in bookings:
		cost += booking.lesson.price

	return round(float(cost) * settings.COMMISSION, 2)