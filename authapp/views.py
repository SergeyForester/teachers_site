import random

from django.contrib import auth
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from authapp.forms import UserForm
from mainapp.models import Profile
from mainapp.utils import *


# Create your views here.

# TODO: remove it
from teachers import settings


@csrf_exempt
def login(request):
	context = context['text'] = get_language(request)
	context['current_lang'] = get_current_language(request)

	if request.method == 'POST':
		print(request.POST)
		user = auth.authenticate(username=request.POST['email'], password=request.POST['password'])
		if user is not None and user.is_active:
			auth.login(request, user)
			if 'api' in request.GET and request.GET['api'] == 'true':
				data = model_to_dict(user)

				p = Profile.objects.get(id=user.id)
				profile = model_to_dict(p)
				profile['avatar'] = settings.HOST_NAME + p.avatar.url
				if p.video:
					profile['video'] = settings.HOST_NAME + p.video.url
				else:
					profile['video'] = ''

				data['profile'] = profile

				return JsonResponse({"code": 200, "user": data})

			return redirect(reverse('main:profile'))
		else:
			if 'api' in request.GET and request.GET['api'] == 'true':
				return JsonResponse({"code": 403})
			return redirect(reverse("auth:login"))

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
