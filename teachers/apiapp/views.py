from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

# Create your views here.
from rest_framework import viewsets

from apiapp.serializers import UserSerializer
from mainapp.models import LessonType


class UsersView(viewsets.ModelViewSet):
	serializer_class = UserSerializer

	def get_queryset(self):
		if self.request.query_params.get("is_teacher") == "true":
			# looking for a teacher
			lesson_types = LessonType.objects.filter(course_type__name__icontains=self.request.query_params.get("course_type", ''),
			                                         user__profile__is_teacher=True)
			queryset = []

			for lesson_type in lesson_types:
				queryset.append(lesson_type.user)

			return queryset

		elif not self.request.query_params.get("is_teacher") == "false":
			# looking only for students
			return User.objects.filter(profile__is_teacher=False)

		else:
			# looking for all users
			return User.objects.all()

class UserView(viewsets.ModelViewSet):
	serializer_class = UserSerializer

	def get_object(self):
		return get_object_or_404(User, pk=self.kwargs['id'])