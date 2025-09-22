from django.urls import path

from .views import *
urlpatterns=[
path('teachers_to_review',Teachers_To_Review.as_view(),name='teachers_to_review'),
    path('review_teacher/<teacher_id>',Load_Review.as_view(),name='load_review'),
    path('update_review_session',Update_Review_Session.as_view(),name='update_review_session'),
    path('close_review_session',Close_Review_Session.as_view(),name='close_review_session')
]