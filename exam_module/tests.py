import datetime

from django.test import TestCase
from django.urls import reverse

from .models import User
from course_module.models import Course
from semester_module.models import Semester,Current_Semester
# Create your tests here.
class Create_Exam_Test(TestCase):
    def setUp(self):

        user1=User(user_type='دانشجو',email='user1@gmail.com',password='1234',national_number='111111111',username='user1')
        user1.set_password('1234')
        user1.save()
        user2=User(user_type='استاد',email='user@gmail.com',username='user2',password='1234',national_number='2222222222')
        user2.set_password('1234')
        user2.save()
        today=datetime.datetime.today()

        sem=Semester(start_date=today+datetime.timedelta(days=5),end_date=today+datetime.timedelta(days=90),semester_type='عادی',
                                    semester_status='انتخاب واحد')
        sem.save()
        cur=Current_Semester(semester_id=sem.id)
        cur.save()
        course=Course(teacher=user2,exam_time=today+datetime.timedelta(days=2),title='course1',credits=3,
                                     department='مهندسی',area_code=11111,capacity=10,semester=sem)
        course.save()
        self.client.login(username=user1.username, password='1234')
        self.user1_status=self.client.get(reverse('create_exam',args=[course.id])).status_code
        self.client.logout()
        self.client.login(username=user2.username,password='1234')
        self.user2_status=self.client.get(reverse('create_exam',args=[course.id])).status_code

    def test(self):
        self.assertNotEqual(self.user1_status,200,msg='user accessed a course that didnt belong to them')
        self.assertEqual(self.user2_status,200,msg='user couldnt access a course of their own')

