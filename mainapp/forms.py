from django import forms

from mainapp.models import Profile, Lesson, LessonType, CourseType


class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('bio', 'location', 'birth_date', 'avatar', 'video')

	def __init__(self, *args, **kwargs):
		super(ProfileForm, self).__init__(*args, **kwargs)


		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'


class TeacherForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ("video", "card_number", "work_day_start", "work_day_end")

	def __init__(self, *args, **kwargs):
		super(TeacherForm, self).__init__(*args, **kwargs)

		hours = [[f"{str(hour)}:{minute}", f"{str(hour)}:{minute}"] for hour in range(24) for minute in ["00", "30"]]

		self.fields['work_day_start'] = forms.ChoiceField(choices=hours)
		self.fields['work_day_end'] = forms.ChoiceField(choices=hours)

		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'


class LessonForm(forms.ModelForm):
	class Meta:
		model = Lesson
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		super(LessonForm, self).__init__(*args, **kwargs)
		self.fields['lesson_type'] = forms.ModelChoiceField(queryset=CourseType.objects.all())
		self.fields['minutes'] = forms.ChoiceField(choices=[['30', '30'], ['60', '60'], ['90', '90'],
		                                                    ['120', '120'], ['150', '150'], ['180', '180'], ])
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'
