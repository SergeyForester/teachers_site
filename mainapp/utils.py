from django.core.mail import send_mail
from django.template.loader import render_to_string

from mainapp.strings import STRINGS


def get_language(request):
	if 'language' not in request.session:
		request.session['language'] = 'en'

	return STRINGS[request.session['language']]


def get_current_language(request):
	return request.session.get('language', 'en')


def send_letter(template, sender, clients, context):
	html_m = render_to_string(template, context)

	return send_mail(
		context['letter_title'], '', sender,
		clients, html_message=html_m, fail_silently=False)


