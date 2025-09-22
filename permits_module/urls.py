from django.urls import path

from .views import *

urlpatterns=[
    path('permits_list',Permits_List.as_view(),name='permits_list'),
    path('ask_for_permit',Ask_For_Permit.as_view(),name='ask_for_permit'),
    path('unconfirmed_permits',UnConfirmed_Permits.as_view(),name='unconfirmed_permits')
]