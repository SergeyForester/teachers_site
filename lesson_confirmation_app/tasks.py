import datetime

from celery import task
from django.contrib.auth.models import User

from apiapp import utils
from lesson_confirmation_app.models import TeacherBill


@task
def check_teachers_bills():
	for teacher in User.objects.filter(profile__is_teacher=True):

		# billing part
		count_from = None
		bills = TeacherBill.objects.filter(teacher=teacher)

		# first case -> teacher has no bills yet
		if not len(bills):
			# then count from teacher_registration_date
			count_from = teacher.profile.teacher_registration_date
		else:
			# second case -> teacher has bills
			# then count from last bill date
			last_bill = bills.latest("created_at")
			count_from = last_bill.created_at

		if count_from:
			# check if a teacher worked for a month
			if count_from + datetime.timedelta(days=30) == datetime.datetime.today():
				# create bill
				TeacherBill.objects.create(
					teacher=teacher,
					pay_by=datetime.datetime.today() + datetime.timedelta(days=1),
					total_amount=utils.cost_of_using(teacher.id)
				)

		# banning part
		if len(bills):
			last_bill = bills.latest("created_at")
			# if teacher didn't pay by a stated time -> ban him
			if last_bill.pay_by < datetime.datetime.today() and not last_bill.is_payed:
				last_bill.teacher.is_active = False
				last_bill.teacher.save()


