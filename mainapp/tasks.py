# Create your tasks here

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_letter(template, sender, clients, context):
	html_m = render_to_string(template, context)

	return send_mail(
		context['letter_title'], '', sender,
		clients, html_message=html_m, fail_silently=False)


