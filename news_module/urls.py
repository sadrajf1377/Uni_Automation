from django.urls import path
from .views import *
urlpatterns=[
    path('',Index_Page.as_view(),name='index')
]