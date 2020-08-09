from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from mainapp.models import Profile, Lesson, LessonType, CourseType, LessonBooking, TeacherTimetableBooking


class ProfileSerializer(ModelSerializer):
	class Meta:
		model = Profile
		fields = "__all__"


class UserSerializer(ModelSerializer):
	profile = ProfileSerializer(read_only=True)

	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'email', 'profile', 'last_login')


class CourseTypeSerializer(ModelSerializer):
	class Meta:
		model = CourseType
		fields = '__all__'


class LessonTypeSerializer(ModelSerializer):
	course_type = CourseTypeSerializer(read_only=True)
	user = UserSerializer(read_only=True)

	class Meta:
		model = LessonType
		fields = '__all__'


class LessonSerializer(ModelSerializer):
	lesson_type = LessonTypeSerializer(read_only=True)

	class Meta:
		model = Lesson
		fields = "__all__"


class LessonBookingSerializer(ModelSerializer):
	lesson = LessonSerializer(read_only=True)

	class Meta:
		model = LessonBooking
		fields = "__all__"


class TeacherTimetableBookingSerializer(ModelSerializer):
	lesson_booking = LessonBookingSerializer(read_only=True)

	class Meta:
		model = TeacherTimetableBooking
		fields = "__all__"
