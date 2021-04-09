import datetime

from mainapp.models import LessonBooking
from teachers import settings


def cost_of_using(user_id=None):
	c_day = datetime.datetime.today() - datetime.timedelta(days=7)
	c_day = c_day.replace(hour=0, minute=0, second=0)

	if user_id:
		bookings = LessonBooking.objects.filter(lesson__lesson_type__user__id=user_id,
		                                        datetime__gte=c_day, is_completed=True)
	else:
		bookings = LessonBooking.objects.filter(datetime__day__gte=c_day, is_completed=True)

	cost = sum([booking.lesson.price for booking in bookings])

	return round(float(cost) * settings.COMMISSION, 2)