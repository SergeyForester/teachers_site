from django.contrib import admin
from mainapp.models import *

# Register your models here.
admin.site.register(CourseType)
admin.site.register(Profile)
admin.site.register(LessonType)
admin.site.register(Lesson)
admin.site.register(LessonBooking)
admin.site.register(TeacherTimetableBooking)
admin.site.register(TeacherTimetable)