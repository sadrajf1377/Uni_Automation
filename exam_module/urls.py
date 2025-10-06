from django.urls import path

from .views import Create_Exam,Update_Exam,Student_Exams,Submit_Exam_Answer,Students_Answers

urlpatterns=[
    path('create_exam/<course_id>',Create_Exam.as_view(),name='create_exam'),
    path('update_exam/<course_id>',Update_Exam.as_view(),name='update_exam'),
    path('student_exams',Student_Exams.as_view(),name='student_exams'),
    path('submit_exam_answer/<course_id>',Submit_Exam_Answer.as_view(),name='submit_exam_answer'),
    path('students_answers/<course_id>',Students_Answers.as_view(),name='students_answers')
]