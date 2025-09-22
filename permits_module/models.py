from django.core.exceptions import ValidationError
from django.db import models
from semester_module.models import Semester
# Create your models here.
from user_module.models import User
class Permit(models.Model):
    types=(('انتخاب واحد','انتخاب واحد'),('ترم آخری','ترم آخری'),('انتخاب واحد خارج از بازه','انتخاب واحد خارج از بازه')
           ,('سنوات','سنوات'))
    permit_type=models.CharField(max_length=40,verbose_name='نوع مجوز',choices=types,null=False,blank=False)
    semester=models.ForeignKey(Semester,on_delete=models.CASCADE,null=False,blank=False,verbose_name='نیمسال مربوطه',related_name='permits')
    creator=models.ForeignKey(User,on_delete=models.CASCADE,null=False,blank=False,verbose_name='کاربر درخواست کننده مجوز',related_name='permits')
    date=models.DateField(verbose_name='تاریخ ایجاد مجوز',auto_now_add=True)
    is_confirmed=models.BooleanField(verbose_name='تیید شده',default=False)
    class Meta:
        indexes=[models.Index(fields=['semester','creator'],name='semester and creator index')]
        constraints=[models.UniqueConstraint(fields=['semester','creator','permit_type'],name='semester and creator uniquness'
                                             ,violation_error_message='این کاربر در حال حاضر مجوزی بااین عنوان در این نیمسال دارد')]
    def save(self,*args):
        if self.id==None:
            user=self.creator
            if user.student_profile.status!='عادی':
                raise ValidationError('به علت عادی نبودن وضعیت دانشجو،امکان ثبت درخواست وجود ندارد')
            if self.semester.semester_status=='بسته':
                raise ValidationError('به علت بسته بودن ترم ترم جاری،امکان ثبت درخواست در این ترم وجود ندارد')
            if self.permit_type=='انتخاب واحد':
                self.is_confirmed=True

        super().save(*args)

