from django.urls import path
from .views import *
urlpatterns=[
    path('',Index_Page.as_view(),name='index'),
    path('create_news',Create_News.as_view(),name='create_news')
]