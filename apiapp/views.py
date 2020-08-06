import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import UpdateView
from googletrans import Translator
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from apiapp.serializers import UserSerializer, LessonSerializer, CourseTypeSerializer, LessonBookingSerializer, \
	TeacherTimetableBookingSerializer, ProfileSerializer
from mainapp.forms import ProfileForm
from mainapp.models import LessonType, Lesson, CourseType, LessonBooking, TeacherTimetableBooking, Profile, \
	TeacherTimetable
from mainapp.strings import STRINGS


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


class UserCoursesView(viewsets.ModelViewSet):
	serializer_class = LessonSerializer

	def get_queryset(self):
		print('User lessons view...')
		lessons = Lesson.objects.filter(lesson_type__user__id=self.kwargs['id'])
		if not len(lessons): return lessons

		if 'lang' in self.request.query_params:
			translator = Translator()

			res = []
			for lesson in lessons:
				lesson.name = translator.translate(lesson.name,
				                                   dest=self.request.query_params['lang']).text.capitalize()
				lesson.lesson_type.course_type.name = translator.translate(lesson.lesson_type.course_type.name,
				                                                           dest=self.request.query_params[
					                                                           'lang']).text.capitalize()
				res.append(lesson)

			return res

		return lessons


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
		return JsonResponse(list(courses), safe=False)


class UserLessonsView(viewsets.ModelViewSet):
	serializer_class = LessonBookingSerializer

	def get_queryset(self):
		queryset = LessonBooking.objects.filter(user__id=self.kwargs['id'])

		if 'completed' in self.request.query_params:
			if self.request.query_params['completed'] == "true":
				queryset = queryset.filter(is_completed=True)
			elif self.request.query_params['completed'] == "false":
				queryset = queryset.filter(is_completed=False)

		return set(queryset.order_by('-lesson__lessonbooking__datetime'))


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

		if 'type' in request.GET:
			if request.GET['type'] == 'redirect':
				return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

	res = model_to_dict(obj)
	return JsonResponse(res, safe=False)
