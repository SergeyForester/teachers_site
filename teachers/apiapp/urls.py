from django.urls import path
from apiapp import views

app_name = "apiapp"

urlpatterns = [
	path('v1/get/users/', views.UsersView.as_view({'get': 'list'})),
	path('v1/get/user/<int:id>/', views.UserView.as_view({'get': 'retrieve'})),
]
