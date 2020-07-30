from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from mainapp.models import CourseType
from mainapp.strings import STRINGS, STRINGS_LANGUAGES
from mainapp.utils import get_language, get_current_language


def main(request):
	context = {}
	context['text'] = get_language(request)
	context['current_lang'] = get_current_language(request)
	context['courses'] = str([course.name for course in CourseType.objects.all()])
	return render(request, 'mainapp/index.html', context)


def change_language(request):
	if 'language' in request.POST and request.POST['language'] in STRINGS_LANGUAGES:
		request.session['language'] = request.POST['language']

	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def teachers_search(request):
	context = {}
	context['text'] = get_language(request)
	context['current_lang'] = get_current_language(request)
	context['course'] = request.POST.get('value', '')

	return render(request, 'mainapp/teachers_search.html', context)


def user_view(request, id):
	context = {}
	context['text'] = get_language(request)
	context['current_lang'] = get_current_language(request)
	context['user_id'] = id

	return render(request, 'mainapp/user_view.html', context)


@login_required(login_url='/auth/login/')
def profile(request):
	context = {}
	context['text'] = get_language(request)
	context['current_lang'] = get_current_language(request)
	context['user_id'] = request.user.id

	return render(request, 'mainapp/profile.html', context)
