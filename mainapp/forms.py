from django import forms

from mainapp.models import Profile, LessonBooking


class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('bio', 'location', 'birth_date', 'avatar', 'video')

	def __init__(self, *args, **kwargs):
		super(ProfileForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'
