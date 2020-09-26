# Create your tasks here
import datetime
import time, pause

from celery import shared_task
from django.contrib.auth.models import User

from mainapp.models import LessonBooking
from mainapp.utils import send_letter, get_language
from teachers import settings


@shared_task
def lesson_complete_confirmation(request, user_id, lesson_booking_id):
	# waiting for the end of lesson
	lesson_booking = LessonBooking.objects.get(id=lesson_booking_id)
	pause.until(lesson_booking.datetime + datetime.timedelta(minutes=lesson_booking.lesson.minutes))

	text = get_language(request)
	confirmation_text = text['booking_confirmation']

	user = User.objects.get(id=user_id)

	# sending email to student
	return send_letter('mainapp/letters/simple_letter.html', settings.EMAIL_HOST_USER,
	                   [user.email],
	                   {
		                   'letter_title': confirmation_text['confirmation_of_the_end'],
		                   'client_name': user.first_name,
		                   'message_title': confirmation_text['confirmation_of_the_end'],
		                   'items': [
					            f'{text["keywords"]["card_number"]}: {lesson_booking.lesson.lesson_type.user.profile.card_number}',
				            ],
				            'message_text': f"{text['keywords']['thank_you_for_the_lesson']}\n{confirmation_text['please_pay_the_teacher']}"
	                   })
