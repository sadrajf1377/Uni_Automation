import datetime
import random

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from user_module.models import User,Teacher_Profile,Student_Profile
from course_module.models import Course,Course_Score
from semester_module.models import Semester,Current_Semester
# Create your tests here.
class Tests_Semester_Reports(TestCase):
    def setUp(self):
        teacher=User(user_type='استاد',username='teacher',email='teacher@teacher.com',national_number='1'*10,password='dds@#$W')
        teacher.save()
        file_data = SimpleUploadedFile(
            "dummy.jpg",  # فقط پسوندش مهمه برای ImageField
            b"fake image bytes",  # داده باینری فرضی
            content_type="image/jpeg"
        )
        teacher_profile=Teacher_Profile(user=teacher,area_code='122',sex='زن',latest_degree='دکتری مستقیم',latest_degree_code='1232',
                                        latest_certificate_picture=file_data,is_approved=True,approval_document=file_data)
        teacher_profile.save()
        student=User(user_type='دانشجو',username='student',email='student@student.com',national_number='2'*10)
        student.set_password('1234')
        student.save()
        student_profile=Student_Profile(user=student,area_code='122',sex='مرد',latest_degree='کارشناسی',latest_degree_code='1232',
                                        latest_certificate_picture=file_data,is_approved=True,approval_document=file_data,current_degree_code='23',
                                        degree='کارشناسی پیوسته')
        student_profile.save()
        courses=[]
        semester=Semester(start_date=datetime.datetime.today(),end_date=datetime.datetime.today()+datetime.timedelta(days=120),
                                         semester_type='عادی')
        semester.save()
        cur=Current_Semester(semester=semester)
        cur.save()
        for i in range(0,10,1):
            course=Course(teacher=teacher,credits=random.randint(1,4),exam_time=datetime.datetime.now()+datetime.timedelta(days=5),
                          capacity=10,semester=semester,title=f'course_{i}',area_code='1232',department='مهندسی')
            course.save()
            course.students.add(student)
            courses.append(course)


        scores=[]
        for co in courses:
            score_value=random.uniform(0,20)
            score=Course_Score(student=student,course=co,score=score_value)
            scores.append(score)
        Course_Score.objects.bulk_create(scores)
        scores_dict={x.score:x.course.credits for x in scores}
        self.client.login(username=student.username,password='1234')
        response=str(self.client.get(reverse('semester_report_card')).content)
        print('content is ',type(response))
        start_index=response.find('<td id="total_avg">')
        result=''
        for i in response[start_index+len('<td id="total_avg">')::]:
          if i=='<':
             break
          result+=i
        self.average=sum([x*y for x,y in scores_dict.items()])/sum(scores_dict.values())
        self.view_average=float(result.replace('\\n','').replace('\\n',''))
    def test(self):
        self.assertEqual(self.average,self.view_average,msg='the view calculated the total average incorrectly!')