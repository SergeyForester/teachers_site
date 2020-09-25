import datetime

import schedule as schedule
from django.contrib import messages
from django.contrib.auth.models import User
from django.core import serializers
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
# Create your views here.
from googletrans import Translator
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apiapp.serializers import UserSerializer, LessonSerializer, LessonBookingSerializer, \
	TeacherTimetableBookingSerializer
from mainapp.forms import ProfileForm, LessonForm, TeacherForm
from mainapp.models import LessonType, Lesson, CourseType, LessonBooking, TeacherTimetableBooking, Profile, \
	TeacherTimetable
from mainapp.tasks import lesson_complete_confirmation
from mainapp.utils import send_letter, get_language
from teachers import settings


class UsersView(viewsets.ModelViewSet):
	serializer_class = UserSerializer

	def get_queryset(self):
		print(f'Query_params: {self.request.query_params}')

		if self.request.query_params.get("is_teacher") == "true":
			print("Looking for a teacher...")

			# looking for a teacher
			users = User.objects.filter(profile__is_teacher=True)

			if "course_type" in self.request.query_params:
				res = []
				for user in users:
					# trying to find teacher
					try:
						teachers = LessonType.objects.filter(
							user=user,
							course_type__name__icontains=self.request.query_params.get("course_type"))

						temp = []
						for i in range(len(teachers)):
							temp.append(teachers[i].user)

						res.extend(set(temp))

					except (LessonType.DoesNotExist, LessonType.MultipleObjectsReturned) as e:
						pass

				users = res

			print(f'users: {users}')

			return users

		elif self.request.query_params.get("is_teacher") == "false":
			# looking only for students
			return User.objects.filter(profile__is_teacher=False)

		else:
			print("All users")
			# looking for all users
			return User.objects.all()


class UserView(viewsets.ModelViewSet):
	serializer_class = UserSerializer

	def get_object(self):
		return get_object_or_404(User, pk=self.kwargs['id'])


class UserCoursesView(APIView):
	serializer_class = LessonSerializer

	def get(self, request, id):
		print('User lessons view...')
		lessons = Lesson.objects.filter(lesson_type__user__id=id)
		if not len(lessons): return Response(LessonSerializer(lessons, many=True).data)

		if 'lang' in self.request.query_params:
			translator = Translator()

			res = []
			for lesson in lessons:
				lesson.name = translator.translate(lesson.name,
				                                   dest=self.request.GET['lang']).text.capitalize()
				lesson.lesson_type.course_type.name = translator.translate(lesson.lesson_type.course_type.name,
				                                                           dest=self.request.GET[
					                                                           'lang']).text.capitalize()
				res.append(lesson)

			return Response(LessonSerializer(res, many=True).data)

		return Response(LessonSerializer(lessons, many=True).data)

	def post(self, request, id):
		# if lesson_type is a course_type
		if 'course_type' in request.GET and request.GET['course_type'] == 'true':
			# if there is no such lesson type
			course_type = CourseType.objects.get(id=request.data['lesson_type'])
			if 'user_id' in request.data:
				lesson_type = LessonType.objects.create(
					course_type=course_type,
					user=User.objects.get(id=request.data['user_id'])).id
			else:
				return Response({"code": 500, "error": 'user_id is required parameter'})

		# TODO: improve this code
		else:
			# or else get it
			lesson_type = LessonType.objects.get(course_type__id=request.POST['lesson_type']).id

		data = request.data.copy()
		data['lesson_type'] = lesson_type

		serializer = LessonSerializer(data=data)
		print(serializer.initial_data)

		# save lesson
		if serializer.is_valid():
			lesson = serializer.save()

			# set user's starting_price
			if lesson.price < lesson.lesson_type.user.profile.starting_price:
				lesson.lesson_type.user.profile.starting_price = lesson_type.price
				lesson.lesson_type.user.profile.save()

			if 'redirect' in request.GET and request.GET['redirect'] == 'true':
				return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

			return Response(LessonSerializer(lesson, many=False).data)

		return Response({"code": 500, "error": 'Data is not valid'})


class UserCourseView(APIView):
	def get(self, request, id, course_id):
		return Response(LessonSerializer(get_object_or_404(Lesson, lesson_type__user__id=id, id=course_id)).data)

	def put(self, request, id, course_id):
		lesson = get_object_or_404(Lesson, lesson_type__user__id=id, id=course_id)
		data = request.data
		serializer = LessonSerializer(instance=lesson, data=data, partial=True)
		if serializer.is_valid(raise_exception=True):
			lesson = serializer.save()
			return Response(LessonSerializer(lesson, many=False).data)
		else:
			return Response({"code": 500, "error": 'Data is not valid'})

	def delete(self, request, id, course_id):
		obj = LessonType.objects.get(id=course_id).delete()
		if 'redirect' in request.GET and request.GET['redirect'] == 'true':
			return HttpResponseRedirect(request.META.get(['HTTP_REFERER'], '/'))

		return Response(LessonSerializer(obj, many=False).data)


class UserTeachersView(viewsets.ModelViewSet):
	serializer_class = UserSerializer

	def get_queryset(self):
		# get all user's bookings
		bookings = LessonBooking.objects.filter(user__id=self.kwargs['id'])

		# set of teachers
		teachers = set()

		# iterate through all users's bookings
		for booking in bookings:
			if booking.lesson.lesson_type.user not in teachers:
				teachers.add(booking.lesson.lesson_type.user)

		return teachers


def courses_view(request):
	courses = CourseType.objects.all()

	if 'lang' in request.GET:
		# translating data
		translator = Translator()

		data = []  # list of dicts: [{"value": "Math", "item":"Математика"}, ...]
		for course in courses:
			obj = {"value": course.name}  # genius entity

			course.name = translator.translate(course.name,
			                                   dest=request.GET['lang']).text.capitalize()

			obj['item'] = course.name  # translated entity
			data.append(obj)

		return JsonResponse(data, safe=False)
	else:
		print([model_to_dict(item) for item in courses])
		return JsonResponse([model_to_dict(item) for item in courses], safe=False)


class UserLessonsView(APIView):
	serializer_class = LessonBookingSerializer

	def get(self, request, id):
		if 'teacher' in self.request.query_params and self.request.query_params['teacher'] == 'true':
			queryset = LessonBooking.objects.filter(lesson__lesson_type__user__id=id)
		else:
			queryset = LessonBooking.objects.filter(user__id=id)

		if 'completed' in self.request.query_params:
			if self.request.query_params['completed'] == "true":
				queryset = queryset.filter(is_completed=True)
			elif self.request.query_params['completed'] == "false":
				queryset = queryset.filter(is_completed=False)

		return Response(
			LessonBookingSerializer(set(queryset.order_by('-lesson__lessonbooking__datetime')), many=True).data)


class UserBookingsView(viewsets.ModelViewSet):
	serializer_class = TeacherTimetableBookingSerializer

	def get_queryset(self):
		date = datetime.datetime.today()
		date = date.replace(hour=0, second=0, minute=0, microsecond=0)
		print(TeacherTimetableBooking.objects.filter(lesson_booking__lesson__lesson_type__user__id=self.kwargs['id'],
		                                             lesson_booking__datetime__gte=date).query)
		return TeacherTimetableBooking.objects.filter(lesson_booking__lesson__lesson_type__user__id=self.kwargs['id'],
		                                              lesson_booking__datetime__gte=date).order_by(
			'-lesson_booking__datetime')


def profile(request, id):
	obj = None

	if request.method == 'POST':
		form = ProfileForm(request.POST, request.FILES, instance=Profile.objects.get(id=id))
		obj = form.save()

		if 'type' in request.GET:
			if request.GET['type'] == 'redirect':
				return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

	res = model_to_dict(obj)
	res['video'] = obj.video.url
	res['avatar'] = obj.avatar.url
	return JsonResponse(res, safe=False)


def create_booking(request):
	obj = None
	# TODO: WARNING this function is a representation of a bad code.

	if request.method == 'POST':
		day = datetime.datetime.strptime(request.POST['day'][4: 15], '%b %d %Y')
		time = request.POST['time'].split(':')
		day = day.replace(hour=int(time[0]), minute=int(time[1]))

		lesson = Lesson.objects.get(id=request.POST['lesson_id'])

		# looking for timetable booking
		bookings_list = LessonBooking.objects.filter(datetime=day, lesson=lesson)
		if len(bookings_list):
			timetable = bookings_list[0]
			if timetable.lesson.is_group and len(bookings_list) + 1 <= timetable.lesson.places:
				# creating one more booking for group lesson
				obj = LessonBooking.objects.create(datetime=day,
				                                   lesson=lesson,
				                                   user=User.objects.get(id=request.POST['user_id']),
				                                   timetable_booking=timetable.timetable_booking)
				if len(bookings_list) + 1 == timetable.lesson.places:
					obj.timetable_booking.status = TeacherTimetableBooking.BOOKED
					obj.timetable_booking.save()

			elif timetable.lesson.is_group and len(
					bookings_list) + 1 > timetable.lesson.places or not timetable.lesson.is_group and len(
				bookings_list) == 1:
				# if there is no enough places in group lesson or lesson is already booked
				if 'type' in request.GET:
					if request.GET['type'] == 'redirect':
						messages.error(request, 'No enough places in lesson')

				return JsonResponse({'code': 500, 'error': 'No enough places in lesson'})

		elif len(bookings_list) == 0:
			# if there is no any bookings and the place is free
			# create timetable booking
			lesson_booking = LessonBooking.objects.create(
				datetime=day,
				lesson=lesson,
				user=User.objects.get(id=request.POST['user_id']))

			ttb = TeacherTimetableBooking.objects.create(
				lesson_booking=lesson_booking,
				timetable=TeacherTimetable.objects.get(user=lesson_booking.lesson.lesson_type.user),
				status=TeacherTimetableBooking.BOOKED if not lesson_booking.lesson.is_group else TeacherTimetableBooking.PENDING)

			lesson_booking.timetable_booking = ttb
			lesson_booking.save()

			text = get_language(request)
			data = text['booking_confirmation']
			keywords = text['keywords']

			# send confirmation letters to user and teacher
			send_letter('mainapp/letters/simple_letter.html', settings.EMAIL_HOST_USER, [lesson_booking.user.email],
			            {
				            'letter_title': data['booking_confirmation'],
				            'client_name': lesson_booking.user.first_name,
				            'message_title': data['you_have_booked_a_lesson'],
				            'items': [
					            f'{keywords["lesson"]}: {lesson_booking.lesson.name}',
					            f'{keywords["time"]}: {str(lesson_booking.datetime)[:-3]}',
					            f'{keywords["teacher"]}: {lesson_booking.lesson.lesson_type.user.first_name}',
					            f'{keywords["price"]}: {lesson_booking.lesson.price} ₽',
				            ],
				            'message_text': data['payment_details']
			            })

			send_letter('mainapp/letters/simple_letter.html', settings.EMAIL_HOST_USER,
			            [lesson_booking.lesson.lesson_type.user.email],
			            {
				            'letter_title': data['new_booking'],
				            'client_name': lesson_booking.user.first_name,
				            'message_title': f'{lesson_booking.user.first_name} {lesson_booking.user.last_name} {data["user_have_booked_a_lesson"]}',
				            'items': [
					            f'{keywords["lesson"]}: {lesson_booking.lesson.name}',
					            f'{keywords["time"]}: {str(lesson_booking.datetime)[:-3]}',
					            f'{keywords["user"]}: {lesson_booking.user.first_name} {lesson_booking.user.last_name}',
					            f'{keywords["price"]}: {lesson_booking.lesson.price} ₽',
				            ],
				            'message_text': ''
			            })

			# scheduling lesson completion mail
			lesson_complete_confirmation.delay(request, lesson_booking.user.id, lesson_booking.id)

		if 'type' in request.GET:
			if request.GET['type'] == 'redirect':
				return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

	res = model_to_dict(obj)
	return JsonResponse(res, safe=False)


def cost_of_using(request):
	cost = 0

	if 'user' in request.GET:
		bookings = LessonBooking.objects.filter(lesson__lesson_type__user__id=request.GET['user'],
		                                        datetime__month=datetime.datetime.now().month)
	else:
		bookings = LessonBooking.objects.filter(datetime__month=datetime.datetime.today().month)

	for booking in bookings:
		cost += booking.lesson.price

	return JsonResponse({'value': round(float(cost) * 0.07, 2)})


def become_a_teacher(request, id):
	if request.method == "POST":
		user = TeacherForm(request.POST, instance=Profile.objects.get(user__id=id)).save()
		user.is_teacher = True
		user.save()

		if 'type' in request.GET:
			if request.GET['type'] == 'redirect':
				return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

		return JsonResponse(model_to_dict(user), safe=False)
	else:
		return JsonResponse({"code": 500, "error": "Invalid request"})