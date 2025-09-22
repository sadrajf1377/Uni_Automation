from django.urls import path

from .views import Create_Semester,Change_Semester,Change_Global_Semester
urlpatterns=[
    path('create_semester',Create_Semester.as_view(),name='create_semester'),
    path('change_semester',Change_Semester.as_view(),name='change_semester'),
    path('cahnge_global_semester',Change_Global_Semester.as_view(),name='change_global_semester')
]