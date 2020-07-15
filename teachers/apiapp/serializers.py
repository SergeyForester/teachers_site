from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from mainapp.models import Profile


class ProfileSerializer(ModelSerializer):
	class Meta:
		model = Profile
		fields = "__all__"


class UserSerializer(ModelSerializer):
	profile = ProfileSerializer(read_only=True)

	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'email', 'profile')
