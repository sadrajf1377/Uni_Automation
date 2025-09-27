from django.urls import path

from .views import *

urlpatterns=[
path('teachers_rating',Teachers_Sorted_By_Ratings.as_view(),name='teachers_ratings'),
    path('load_profile_filters',Load_Profiles_Filters.as_view(),name='load_profile_filters'),
    path('view_teacher_profiles/<department>/<rank>',UnApproved_Teachers.as_view(),name='view_unapproved_teachers'),
    path('view_student_profiles/<department>/<degree>',UnApproved_Students.as_view(),name='view_unapproved_students'),
    path('view_employee_profiles/<role>',UnApproved_Employees.as_view(),name='view_unapproved_employees')
   ,path('update_profile',Update_Profile.as_view(),name='update_profile'),
    path('departments',Departments_List.as_view(),name='departments_list'),
    path('approve_user/<profile_id>/<profile_type>',Approve_User.as_view(),name='approve_user')
]