from django.urls import path

from .views import *

urlpatterns=[
    path('report_card',Total_Report_Card.as_view(),name='report_card'),
    path('semester_report_card',View_Semester_Report.as_view(),name='semester_report_card'),
    path('schedule',My_Schedule.as_view(),name='weekly_schedule'),
    path('courses_list/<title>/<department>/<degree>/<course_type>',Current_Semester_Courses.as_view(),name='courses_list'),
    path('teacher_courses',Teacher_Courses.as_view(),name='teacher_courses'),
    path('course_details/<course_id>',Course_Details.as_view(),name='view_course_details'),
    path('update_course_details/<course_id>',Update_Courses_Details.as_view(),name='update_course_details'),
    path('pick_course/<course_id>',Pick_Courses.as_view(),name='pick_course'),
    path('delete_course/<course_id>',Delete_Course.as_view(),name='delete_course'),
    path('exams_shecduele',Student_Exams.as_view(),name='exams_schedule'),
    path('top_students',Top_Students.as_view(),name='top_students')

]