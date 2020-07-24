from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from mainapp.models import Profile, Lesson, LessonType, CourseType


class ProfileSerializer(ModelSerializer):
	class Meta:
		model = Profile
		fields = "__all__"


class UserSerializer(ModelSerializer):
	profile = ProfileSerializer(read_only=True)

	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'email', 'profile')


class CourseTypeSerializer(ModelSerializer):
	class Meta:
		model = CourseType
		fields = '__all__'


class LessonTypeSerializer(ModelSerializer):
	course_type = CourseTypeSerializer(read_only=True)

	class Meta:
		model = LessonType
		fields = '__all__'


class LessonSerializer(ModelSerializer):
	lesson_type = LessonTypeSerializer(read_only=True)

	class Meta:
		model = Lesson
		fields = "__all__"
