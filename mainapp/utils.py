from mainapp.strings import STRINGS


def get_language(request):
	if 'language' not in request.session:
		request.session['language'] = 'en'

	return STRINGS[request.session['language']]


def get_current_language(request):
	return request.session.get('language', 'en')


