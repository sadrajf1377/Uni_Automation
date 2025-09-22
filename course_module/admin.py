from django.contrib import admin
from .models import Course,Class_Times,Course_Score
# Register your models here.
class Course_View(admin.ModelAdmin):
    list_display = ['title','teacher','semester']
    list_display_links = ['title']
admin.site.register(Course,Course_View)
admin.site.register(Class_Times)
admin.site.register(Course_Score)