from django.shortcuts import render, redirect
from teachers import settings


def teacher_profile(request):
	return redirect(settings.STORE_HOST + "auth/login/?next=/profile/seller/")