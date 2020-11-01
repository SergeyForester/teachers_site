import datetime

from celery import task
from django.contrib.auth.models import User
from django.urls import reverse

from apiapp import utils
from lesson_confirmation_app.models import TeacherBill
from mainapp.tasks import send_letter
from mainapp.utils import get_language
from teachers import settings


# @periodic_task(run_every=crontab(minute=1))
@task
def check_teachers_bills():
	teachers_ = User.objects.filter(profile__is_teacher=True)
	today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

	created_bills = 0
	banned_teachers = 0

	print("Checking teachers' bills")
	print(f"{len(teachers_)} to check")

	for teacher in teachers_:
		# billing part
		bills = TeacherBill.objects.filter(teacher=teacher)

		# first case -> teacher has no bills yet
		if not len(bills):
			# then count from teacher_registration_date
			count_from = teacher.profile.teacher_registration_date.replace(hour=0, minute=0, second=0, microsecond=0)
		else:
			# second case -> teacher has bills
			# then count from last bill date
			last_bill = bills.latest("-created_at")
			count_from = last_bill.created_at.replace(hour=0, minute=0, second=0, microsecond=0)

		count_from = count_from.replace(tzinfo=None)
		print(f'<{teacher.username}>: Count from: {count_from}')

		if count_from:
			# check if a teacher worked for a week
			if count_from + datetime.timedelta(days=1) == today:
				total_amount = utils.cost_of_using(teacher.id)

				if total_amount < 150:
					total_amount = 150

				# create bill
				bill = TeacherBill.objects.create(
					teacher=teacher,
					pay_by=today + datetime.timedelta(days=1),
					total_amount=total_amount
				)
				print("Bill has been created")

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
						                  f'{usage_fee_text["pay_by"]} {bill.pay_by}',
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

				created_bills += 1

		# banning part
		if len(bills):
			last_bill = bills.latest("created_at")
			# if teacher didn't pay by a stated time -> ban him
			if last_bill.pay_by.replace(tzinfo=None) < today \
					and len(TeacherBill.objects.filter(teacher=teacher, is_payed=False)):
				last_bill.teacher.is_active = False
				last_bill.teacher.save(compress=False)
				banned_teachers += 1

	print(f"Created bills: {created_bills}")
	print(f"Banned teachers: {banned_teachers}")

# @celeryd_init.connect
# def check_bills_on_init(sender=None, conf=None, **kwargs):
# 	check_teachers_bills.delay()
