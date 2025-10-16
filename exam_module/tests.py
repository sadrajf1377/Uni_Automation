import datetime

from django.test import TestCase
from django.urls import reverse

from user_module.models import User
from.models import Exam
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


class Test_Students_Exams_List(TestCase):
    def setUp(self):
        student=User(user_type='دانشجو',username='student',national_number='1'*10)
        student.set_password('1234')
        student.save()
        teacher=User(user_type='استاد',username='teacher',national_number='2'*10,password='1234')
        teacher.save()
        today=datetime.datetime.today()
        semester=Semester(start_date=today,end_date=today+datetime.timedelta(days=60),semester_type='عادی')
        semester.save()
        cur = Current_Semester(semester_id=semester.id)
        cur.save()
        course = Course(teacher=teacher, exam_time=today + datetime.timedelta(days=2), title='course1', credits=3,
                        department='مهندسی', area_code=11111, capacity=10, semester=semester)
        course.save()
        course.students.add(student)
        self.client.login(username=student.username,password='1234')
        self.course_id=course.id
        exam=Exam(start_time=datetime.datetime.now()+datetime.timedelta(days=1),end_time=datetime.datetime.now()+datetime.timedelta(days=2),course_id=self.course_id)
        exam.save()
        self.exams_list=self.client.get(reverse('student_exams'))
        print('exams list content',self.course_id)
    def test(self):
        self.assertContains(self.exams_list,f'<tr id="exam_{self.course_id}">')

