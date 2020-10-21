from mainapp.strings import STRINGS


def get_language(request=None, lang=None):
	if lang: return STRINGS[lang]

	if 'language' not in request.session:
		request.session['language'] = 'ru'

	return STRINGS[request.session['language']]


def get_current_language(request):
	return request.session.get('language', 'ru')


