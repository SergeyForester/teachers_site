import random

from django.contrib import auth
from django.shortcuts import render, redirect
from django.urls import reverse

from authapp.forms import UserForm
from mainapp.utils import *


# Create your views here.
def login(request):
	context = context['text'] = get_language(request)
	context['current_lang'] = get_current_language(request)

	if request.method == 'POST':
		user = auth.authenticate(username=request.POST['email'], password=request.POST['password'])
		if user is not None and user.is_active:
			auth.login(request, user)
			return redirect(reverse('main:profile'))

	return render(request, 'authapp/login.html', context)

def sign_up(request):
	context = context['text'] = get_language(request)
	context['current_lang'] = get_current_language(request)
	context['form'] = UserForm()

	if request.method == 'POST':
		form = UserForm(request.POST)
		user = form.save(commit=False)

		user.username = user.first_name + str(random.randint(1, 999999))
		user.save()

		# save and login
		if user is not None:
			auth.login(request, user)
			return redirect(reverse('main:profile'))

	return render(request, 'authapp/sign_up.html', context)


def logout(request):
	auth.logout(request)
	return redirect('/')