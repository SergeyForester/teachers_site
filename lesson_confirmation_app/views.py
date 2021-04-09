import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from yandex_checkout import Configuration, Payment

from lesson_confirmation_app.models import TeacherBill
from mainapp.models import LessonBooking
from mainapp.utils import get_current_language, get_language
from mainapp.tasks import send_letter
from teachers import settings

Configuration.configure('707095', 'test_ZlfSv-xgCIBSKohaHNcifWgXrkaO3CTfEtt7sbj5FWk')

@login_required(login_url="/auth/login/")
def confirm_the_end_of_the_lesson(request, id):
	if request.method == 'POST':
		lesson_booking = get_object_or_404(LessonBooking, id=id)

		if lesson_booking.user != request.user:
			return redirect("/")

		if 'finished' in request.POST and request.POST['finished']:
			lesson_booking.is_completed = True
		else:
			lesson_booking.is_completed = False

		lesson_booking.save()

		user = lesson_booking.lesson.lesson_type.user
		text = get_language(request)
		confirmation_text = text['booking_confirmation']

		send_letter.delay('mainapp/letters/simple_letter.html', settings.EMAIL_HOST_USER,
		            [user.email],
		            {
			            'letter_title': confirmation_text['confirmation_of_the_end'],
			            'client_name': user.first_name,
			            'message_title': confirmation_text['confirmation_of_the_end'],
			            'message_text': f"{text['keywords']['thank_you_for_the_lesson']}\n{lesson_booking.user.first_name + ' ' + confirmation_text['student_confirmed_the_lesson']}",
		            })
		return redirect('/')
	else:
		context = {'text': get_language(request), 'current_lang': get_current_language(request),
		           'user_id': request.user.id}
		return render(request, 'lesson_confirmation_app/confirmation.html', context)


@login_required(login_url='/auth/login/')
def pay_for_using(request, id):
	bill = get_object_or_404(TeacherBill, id=id)

	if bill.teacher.id == request.user.id:
		if request.method == "POST":
			date = request.POST['expiry'].split(" / ")

			payment = Payment.create({
				"amount": {
					"value": float(bill.total_amount),
					"currency": "RUB"
				},
				"payment_method_data": {
					"type": "bank_card",
					"card": {
						"number": request.POST['number'].replace(" ", ''),
						"expiry_year": "20" + date[1],
						"expiry_month": date[0],
						"csc": request.POST['cvc'],
						"cardholder": request.POST['name'],
					}
				},
				"confirmation": {
					"type": "redirect",
					"return_url": f"https://{settings.HOST_NAME}"
				},
				"description": f"Оплата за пользование системой №{bill.id}"
			}, str(uuid.uuid4()))

			payment_id = payment.id
			print(payment_id)

			response = Payment.capture(
				payment_id,
				{
					"amount": {
						"value": float(bill.total_amount),
						"currency": "RUB"
					}
				}, str(uuid.uuid4())
			)

			# get confirmation url
			bill.is_payed = True
			bill.save()

			if not len(TeacherBill.objects.filter(teacher=bill.teacher, is_payed=False)):
				bill.teacher.is_active = True
				bill.teacher.save()


			messages.success(request, get_language(request)["keywords"]["success"])
			return redirect("/")

		return render(request, 'lesson_confirmation_app/pay_usage_fee.html',
	              {'text': get_language(request),
	               'current_lang': get_current_language(request),
	               "id": id})
	else:
		return redirect("/")

