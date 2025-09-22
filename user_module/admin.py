from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Teacher_Profile)
admin.site.register(Student_Profile)
admin.site.register(Employee_Profile)
