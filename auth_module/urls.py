from django.urls import path

from .views import *
urlpatterns=[
    path('login',Login.as_view(),name='login'),
    path('temp_code_login',Login_With_Temp_Code.as_view(),name='login_with_temp_code'),
    path('signup',Signup.as_view(),name='signup'),
    path('activate_account/<act_code>',Activate_Account.as_view(),name='activate_account'),
    path('ask_for_temp_pass',Generate_New_Temp_Code.as_view(),name='ask_for_temp_pass')
]
