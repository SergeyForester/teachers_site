# Create your tasks here
import datetime
import time, pause

from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

from mainapp.models import LessonBooking
from mainapp.utils import get_language
from teachers import settings


@shared_task
def send_letter(template, sender, clients, context):
	html_m = render_to_string(template, context)

	return send_mail(
		context['letter_title'], '', sender,
		clients, html_message=html_m, fail_silently=False)


@shared_task
def lesson_complete_confirmation(user_id, lesson_booking_id):
	# waiting for the end of lesson
	lesson_booking = LessonBooking.objects.get(id=lesson_booking_id)

	timedelta_ = lesson_booking.datetime.replace(tzinfo=None) - datetime.datetime.now()

	time_to_sleep = int(timedelta_.total_seconds()) + int(lesson_booking.lesson.minutes * 60)
	print(time_to_sleep)
	time.sleep(time_to_sleep)

	text = get_language(lang="ru")
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
		                   'message_text': f"{text['keywords']['thank_you_for_the_lesson']}\n{confirmation_text['please_pay_the_teacher']}",
		                   "link": {
			                   'href': settings.HOST_NAME + str(reverse("lessons:confirmation",
			                                                                     kwargs={"id": lesson_booking.id}))[1:]
		                   },
		                        "text": text["keywords"]["confirm"]
	                   })
