from django.urls import path

from mainapp import views

app_name = "mainapp"

urlpatterns = [
	path("", views.main, name="main"),
	path("change/language/", views.change_language, name="change_language"),
	path("teachers/", views.teachers_search, name="teachers_search"),
	path("user/<int:id>/", views.user_view, name="user"),
	path("profile/", views.profile, name="profile"),
	path("profile/teacher/", views.profile_teacher, name="profile_teacher"),
	path("profile/teacher/sign_up/", views.become_a_teacher, name="become_a_teacher"),
]