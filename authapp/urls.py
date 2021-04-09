from django.urls import path

from authapp import views

app_name = "authapp"

urlpatterns = [
	path("login/", views.login, name="login"),
	path("join/", views.sign_up, name="sign_up"),
	path("logout/", views.logout, name="logout"),
]