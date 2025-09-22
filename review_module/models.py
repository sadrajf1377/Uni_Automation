from django.core.exceptions import ValidationError
from django.db import models
from user_module.models import User
from semester_module.models import Semester
class Review_Question(models.Model):
    q_text=models.TextField(verbose_name='متن سوال',null=False,blank=False)
    def __str__(self):
        return self.q_text


class Review_Session(models.Model):
    teacher=models.ForeignKey(User,on_delete=models.CASCADE,null=False,blank=False,related_name='teacher_review',db_index=True)
    student=models.ForeignKey(User,on_delete=models.CASCADE,null=False,blank=False,related_name='student_reviews',db_index=True)
    session_closed=models.BooleanField(verbose_name='نظر سنجی تایید نهایی شده است یا خیر؟',default=False)
    semester=models.ForeignKey(Semester,on_delete=models.CASCADE,null=True,blank=True,related_name='semester_reviews')
    def save(self,*args,**kwargs):
        check_student=self.student.user_type == 'دانشجو' and self.student.student_profile.is_approved
        check_teacher=self.teacher.user_type == 'استاد' and self.teacher.teacher_profile.is_approved
        can_review_teacher=self.student.attending_courses.filter(semester=self.semester,teacher=self.teacher)
        if not (check_teacher and check_student):
            raise ValidationError('ثبت کننده امتیاز می بایست دانشجوی تاییدشده و دریافت کننده امتیاز می بایست استاد تایید شده باشد')
        if not can_review_teacher:
            raise ValidationError('دانشجو به علت درس نداشتن با این استاد در نمیسال انتخابی مجاز به ارزیابی ایشان نمی باشد')
        generate_reviews=self.id==None
        super().save(*args,**kwargs)
        if generate_reviews:
            obs = []
            ids=list(Review_Question.objects.all().values_list('id', flat=True))
            for id in ids:
                print('iterated review')
                ob = Reviews(question_id=id, session_id=self.id)
                obs.append(ob)
            Reviews.objects.bulk_create(obs)

    class Meta:
        constraints=[models.UniqueConstraint(fields=['teacher','student','semester'],name='check student and teacher pair uniquness',
                                             violation_error_message='این دانشجو قبلا مدلی برای امتیاز دهی به این استاد در این نیمسال ایجاد کرده است')]



class Reviews(models.Model):
    question=models.ForeignKey(Review_Question,on_delete=models.CASCADE,null=False,blank=False,verbose_name='سوال')
    review_choices=(('عالی','عالی'),('خوب','خوب'),('متوسط','متوسط'),('ضعیف','ضعیف'),('خیلی ضعیف','خیلی ضعیف'))
    review=models.CharField(max_length=20,choices=review_choices,verbose_name='نظر کاربر',default='متوسط')
    session=models.ForeignKey(Review_Session,on_delete=models.CASCADE,null=False,blank=False,related_name='reviews',db_index=True)
# Create your models here.
