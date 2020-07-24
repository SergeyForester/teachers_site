from mainapp.strings import STRINGS


def get_language(request):
	# if language was already selected:
	if 'language' in request.session:
		return STRINGS[request.session['language']]
	else:  # set default language
		request.session['language'] = 'en'

def get_current_language(request):
	return request.session.get('language', 'en')