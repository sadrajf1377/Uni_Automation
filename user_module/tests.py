import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from semester_module.models import Semester,Current_Semester
from .models import User,Teacher_Profile,Student_Profile,Employee_Profile
# Create your tests here.
def generate_profiles():
    president = User(user_type='استاد', username='teacher', email='teacher@teacher.com', national_number='1' * 10, )
    president.set_password('1234')
    president.save()
    file_data = SimpleUploadedFile(
        "dummy.jpg",
        b"fake image bytes",
        content_type="image/jpeg"
    )
    pr_profile = Teacher_Profile(user=president, area_code='122', sex='زن', latest_degree='دکتری مستقیم',
                                 latest_degree_code='1232',
                                 latest_certificate_picture=file_data, is_approved=True,
                                 approval_document=file_data, role='رییس دانشکده',department='مهندسی',rank='استاد تمام')
    pr_profile.save()
    student=User(user_type='دانشجو', username='student', email='student@teacher.com', national_number='2' * 10,password='1234')
    student.save()
    student_profile=Student_Profile(user=student, area_code='122', sex='زن', latest_degree='کارشناسی',
                                 latest_degree_code='1232',
                                 latest_certificate_picture=file_data, is_approved=False,
                                 approval_document=file_data,department='مهندسی',degree='کارشناسی ارشد ناپیوسته')
    student_profile.save()
    teacher = User(user_type='استاد', username='teacher2', email='teacher2@teacher.com', national_number='3' * 10,password='1234')
    teacher.save()
    teacher_profile = Teacher_Profile(user=teacher, area_code='122', sex='زن', latest_degree='دکتری مستقیم',
                                 latest_degree_code='1232',
                                 latest_certificate_picture=file_data, is_approved=False,
                                 approval_document=file_data, role='عادی',department='مهندسی',rank='استادیار')
    teacher_profile.save()
    return {'teacher_id':teacher.id,'student_id':student.id}



class Test_Unapproved_Users_Search(TestCase):
    def setUp(self):
       data=generate_profiles()
       self.teacher_id=data['teacher_id']
       self.student_id=data['student_id']
       self.client.login(username='teacher',password='1234')
       semester=Semester(semester_type='عادی',start_date=datetime.datetime.today(),end_date=datetime.datetime.today()+datetime.timedelta(days=7))
       semester.save()
       cur_sem=Current_Semester(semester=semester)
       cur_sem.save()
       self.teachers_unapproved_profiles=str(self.client.get(reverse('view_unapproved_teachers',args=['مهندسی','استادیار'])).content.decode('utf-8'))
       self.students_unapproved_profiles=str(self.client.get(reverse('view_unapproved_students',args=['مهندسی','کارشناسی ارشد ناپیوسته'])).content.decode('utf-8'))
    def test(self):
        self.assertIn(f'<td id="{self.teacher_id}">',self.teachers_unapproved_profiles,msg='didnt bring the unapproved teacher in the show unapproved teachers view')
        self.assertIn(f'<td id="{self.student_id}">',self.students_unapproved_profiles,msg='didnt show an unaproved student in the unapproved students view')

