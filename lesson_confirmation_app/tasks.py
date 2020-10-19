import datetime

from celery import task
from django.contrib.auth.models import User
from django.urls import reverse

from apiapp import utils
from lesson_confirmation_app.models import TeacherBill
from mainapp.tasks import send_letter
from mainapp.utils import get_language
from teachers import settings


@task
def check_teachers_bills():
	teachers_ = User.objects.filter(profile__is_teacher=True)

	print("Checking teachers' bills")
	print(f"{len(teachers_)} to check")

	for teacher in teachers_:
		# billing part
		bills = TeacherBill.objects.filter(teacher=teacher)

		# first case -> teacher has no bills yet
		if not len(bills):
			# then count from teacher_registration_date
			count_from = teacher.profile.teacher_registration_date
		else:
			# second case -> teacher has bills
			# then count from last bill date
			last_bill = bills.latest("-created_at")
			count_from = last_bill.created_at

		if count_from:
			# check if a teacher worked for a month
			if count_from + datetime.timedelta(days=7) == datetime.datetime.today():
				total_amount = utils.cost_of_using(teacher.id)

				# create bill
				bill = TeacherBill.objects.create(
					teacher=teacher,
					pay_by=datetime.datetime.today() + datetime.timedelta(days=1),
					total_amount=total_amount
				)
				# send email with bill
				text = get_language(lang="ru")
				usage_fee_text = text['system_usage_fee']

				send_letter.delay('mainapp/letters/simple_letter.html', settings.EMAIL_HOST_USER,
				                  [teacher.email],
				                  {
					                  'letter_title': usage_fee_text['system_usage_fee'],
					                  'client_name': teacher.first_name,
					                  'message_title': usage_fee_text['system_usage_fee'],
					                  'items': [
						                  f'{usage_fee_text["total_amount"]}: {total_amount}',
					                  ],
					                  'message_text': "",
					                  "link": {
						                  'href': settings.HOST_NAME + str(reverse("lessons:pay_for_using",
						                                                        kwargs={
							                                                        "id": bill.id
						                                                        }))[1:]
					                  },
					                  "text": text["keywords"]["pay"]
				                  })

		# banning part
		if len(bills):
			last_bill = bills.latest("created_at")
			# if teacher didn't pay by a stated time -> ban him
			if last_bill.pay_by < datetime.datetime.today() and not last_bill.is_payed:
				last_bill.teacher.is_active = False
				last_bill.teacher.save()
