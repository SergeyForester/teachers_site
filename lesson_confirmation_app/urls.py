from django.urls import path

from lesson_confirmation_app import views

app_name = "lesson_confirmation_app"

urlpatterns = [
	path('confirmation/<int:id>/', views.confirm_the_end_of_the_lesson, name="confirmation"),
	path('pay_for_using/<int:id>/', views.pay_for_using, name="pay_for_using"),
]