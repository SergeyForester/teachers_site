from django.urls import path

from storeapp import views

app_name = "storeapp"

urlpatterns = [
	path("profile/", views.teacher_profile, name="teacher_profile")
]