from django.urls import path
from apiapp import views

app_name = "apiapp"

urlpatterns = [
	path('v1/users/', views.UsersView.as_view({'get': 'list'})),
	path('v1/users/<int:id>/', views.UserView.as_view({'get': 'retrieve'})),
	path('v1/users/<int:id>/courses/', views.UserCoursesView.as_view()),
	path('v1/users/<int:id>/courses/<int:course_id>/', views.UserCourseView.as_view()),
	path('v1/users/<int:id>/teachers/', views.UserTeachersView.as_view({'get': 'list'})),
	path('v1/users/<int:id>/lessons/', views.UserLessonsView.as_view()),
	path('v1/users/<int:id>/bookings/', views.UserBookingsView.as_view({'get': 'list'})),
	path('v1/users/<int:id>/profile/', views.profile),
	path('v1/users/<int:id>/teaching/start/', views.become_a_teacher),

	path('v1/courses/', views.courses_view),

	path('v1/management/cost_of_using/', views.cost_of_using),

	path('v1/bookings/create/', views.create_booking),

]
