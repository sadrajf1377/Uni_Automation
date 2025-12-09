from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from user_module.models import User,Student_Profile
# Create your tests here.
class Test_Ticket_Creation(TestCase):
    def setUp(self):
        student = User(user_type='دانشجو', username='student', email='student@student.com', national_number='2' * 10)
        student.set_password('1234')
        student.save()
        file_data = SimpleUploadedFile(
            "dummy.jpg",  # فقط پسوندش مهمه برای ImageField
            b"fake image bytes",  # داده باینری فرضی
            content_type="image/jpeg"
        )
        student_profile = Student_Profile(user=student, area_code='122', sex='مرد', latest_degree='کارشناسی',
                                          latest_degree_code='1232',
                                          latest_certificate_picture=file_data, is_approved=True,
                                          approval_document=file_data, current_degree_code='23',
                                          degree='کارشناسی پیوسته')
        student_profile.save()
        self.client.login(username='student',password='1234')
        self.view_status=self.client.post(reverse('create_new_ticket'),data={'title':'تیکت جدید','subject':'ثبت مجوز'}).status_code
    def test(self):
        self.assertEqual(self.view_status,201,msg='failed to create ticket for an authenticated user')

