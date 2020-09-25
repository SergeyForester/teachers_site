from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from mainapp.forms import ProfileForm, LessonForm, TeacherForm
from mainapp.models import CourseType, Profile
from mainapp.strings import STRINGS_LANGUAGES
from mainapp.utils import get_language, get_current_language


def main(request):
	context = {'text': get_language(request), 'current_lang': get_current_language(request),
	           'courses': str([course.name for course in CourseType.objects.all()])}
	return render(request, 'mainapp/index.html', context)


def change_language(request):
	if 'language' in request.POST and request.POST['language'] in STRINGS_LANGUAGES:
		request.session['language'] = request.POST['language']

	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def teachers_search(request):
	context = {'text': get_language(request), 'current_lang': get_current_language(request),
	           'course': request.POST.get('value', '')}

	return render(request, 'mainapp/teachers_search.html', context)


def user_view(request, id):
	context = {'text': get_language(request), 'current_lang': get_current_language(request), 'user_id': id}

	return render(request, 'mainapp/user_view.html', context)

@login_required(login_url='/auth/login/')
def become_a_teacher(request):
	context = {'text': get_language(request), 'current_lang': get_current_language(request), 'user_id': request.user.id}

	context['form'] = TeacherForm(instance=Profile.objects.get(user=request.user))

	return render(request, 'mainapp/teacher_sign_up.html', context)

@login_required(login_url='/auth/login/')
def profile(request):
	context = {'text': get_language(request), 'current_lang': get_current_language(request), 'user_id': request.user.id}

	form = ProfileForm(instance=Profile.objects.get(user=request.user))
	context['profile_form'] = form

	return render(request, 'mainapp/profile.html', context)


def profile_teacher(request):
	if not request.user.profile.is_teacher:
		return redirect('/')

	context = {'text': get_language(request), 'current_lang': get_current_language(request), 'user_id': request.user.id,
	           'lesson_form': LessonForm()}

	return render(request, 'mainapp/profile_teacher.html', context)
