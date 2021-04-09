from django.contrib.auth.models import User
from rest_framework import serializers
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
	class Meta:
		model = Lesson
		fields = "__all__"

	def create(self, validated_data):
		return Lesson.objects.create(**validated_data)

	def update(self, instance, validated_data):
		instance.lesson_type = validated_data.get('lesson_type', instance.lesson_type)
		instance.name = validated_data.get('name', instance.name)
		instance.price = validated_data.get('price', instance.price)
		instance.minutes = validated_data.get('minutes', instance.minutes)
		instance.is_group = validated_data.get('is_group', instance.is_group)
		instance.places = validated_data.get('places', instance.places)
		instance.save()
		return instance

	def to_representation(self, instance):
		self.fields['lesson_type'] = LessonTypeSerializer(read_only=True)
		return super(LessonSerializer, self).to_representation(instance)


class LessonBookingSerializer(ModelSerializer):
	lesson = LessonSerializer(read_only=True)
	user = UserSerializer(read_only=True)

	class Meta:
		model = LessonBooking
		fields = "__all__"


class TeacherTimetableBookingSerializer(ModelSerializer):
	lesson_booking = LessonBookingSerializer(read_only=True)

	class Meta:
		model = TeacherTimetableBooking
		fields = "__all__"
