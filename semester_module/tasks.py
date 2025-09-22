from celery import shared_task
from django.core.cache import caches
from .models import Current_Semester
status_choices=(('شروع نشده','0'),('انتخاب واحد','1'),('جاری','2'),('امتحان','3'),('بسته','4'))
@shared_task
def start_semester():
    Current_Semester.semester.status=status_choices[1][0]
    Current_Semester.semester.save()
    change_status_to_normal.delay(countdown=3600*24*14)


@shared_task
def change_status_to_normal():
    Current_Semester.semester.status=status_choices[2][0]
    Current_Semester.semester.save()
    duration=Current_Semester.semester.duration()
    change_semester_to_exams.delay(countdown=duration)


@shared_task
def change_semester_to_exams():
    Current_Semester.semester.status = status_choices[3][0]
    Current_Semester.semester.save()
    change_semester_to_close.delay(countdown=3600 * 24 * 14)

@shared_task
def change_semester_to_close():
    Current_Semester.semester.status=status_choices[4][0]
    Current_Semester.semester.save()







