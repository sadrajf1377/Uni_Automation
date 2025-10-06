import datetime

from django.core.exceptions import ValidationError
from django.db import models
from course_module.models import Course
from user_module.models import User
# Create your models here.
class Exam(models.Model):
    course=models.OneToOneField(Course,on_delete=models.CASCADE,null=False,blank=False,related_name='exam',verbose_name='این امتحان مربوط به کدام درس می باشد')
    start_time=models.DateTimeField(verbose_name='زمان شروع امتحان')
    end_time=models.DateTimeField(verbose_name='زمان پایان امتحان')


def exam_file_validator(file):
    if file.size >500000:
        raise ValidationError('حجم فایل آپلود شده باید کمتر از 500 کیلوبایت باشد')

class Exam_Answer(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE,null=False,blank=False,related_name='exams_answers',verbose_name='کدام دانشجو پاسخ را ایجاد کرده است')
    exam=models.ForeignKey(Exam,on_delete=models.CASCADE,null=False,blank=False,related_name='answers',db_index=True,verbose_name='این پاسخ مربوط به کدام امتحان می باشد')
    submit_date=models.DateTimeField(verbose_name='زمان ثبت پاسخ',auto_now_add=True)
    description=models.TextField(verbose_name='توضیحات مربوط به امتحان (اختیاری)',null=True,blank=True)
    file=models.FileField(upload_to='students_answerss',verbose_name='فایل پاسخنامه',null=False,blank=False,validators=[exam_file_validator])
    class Meta:
        constraints=[models.UniqueConstraint(fields=['author','exam'],name='author and exam uniquness',violation_error_message='این دانشجو قبلا برای این درس پاسخ ارسال کرده است')]

