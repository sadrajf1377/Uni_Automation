from django.core.exceptions import ValidationError
from django.db import models
from user_module.models import User,Student_Profile,Teacher_Profile,Employee_Profile
user_profiles={'دانشجو':Student_Profile,'استاد':Teacher_Profile,'کارمند یا کارشناس':Employee_Profile}
# Create your models here.


def ticket_image_validator(image):
    if image.size>=50000:
        raise ValidationError('اندازه تصویر بزرگ است')

class Ticket(models.Model):
    title=models.CharField(max_length=100,verbose_name='عنوان تیکت',null=False,blank=False,error_messages={'null':'عنوان تیک باید نوشته شود'})
    choices=(('ثبت مجوز','ثبت مجوز'),('انتخاب درس','انتخاب درس'),('حذف درس','حذف درس'),('ثبت ارزشیابی','ثبت ارزشیابی'),('ثبت نمره','ثبت نمره')
             ,('تایید حساب کاربری','تایید حساب کاربری'),('---','---'))
    subject=models.CharField(max_length=50,choices=choices,verbose_name='دسته بندی تیکت',null=False,blank=False,error_messages={'null':'دسته بندی باید مشخص شود'})
    creator=models.ForeignKey(User,on_delete=models.CASCADE,null=False,blank=False,db_index=True,related_name='tickets',verbose_name='کاربر ایجاد کننده تیکت',
                              error_messages={'null':'کاربر ایجاد کننده تیکت مشخص نشده است!'})
    date=models.DateField(auto_now_add=True,verbose_name='تاریخ ایجاد تیکت')
    is_closed=models.BooleanField(verbose_name='آیا تیکت بسته شده است',default=False)
    def save(self,*args):
        if self.id==None:
            u_type = self.creator.user_type
            if not user_profiles[u_type].objects.filter(user_id=self.creator.id,is_approved=True).exists():
                raise ValidationError('برای ایجاد تیکت باید حساب شما تایید شده باشد')
        else:
            cond=self.creator!=Ticket.objects.get(id=self.id).creator
            if not cond:
                raise ValidationError('امکان تغییر کاربر تیکت پس از ایجاد تیکت وجود ندارد!')



        super().save(*args)

class Ticket_Message(models.Model):
    text=models.TextField(verbose_name='متن پیام')
    date=models.DateTimeField(auto_now_add=True,verbose_name='زمان ایجاد پیام')
    thumb=models.ImageField(upload_to='ticket_thumbs',validators=[ticket_image_validator],verbose_name='تصویر (اختیاری)',null=True,blank=True)
    class Meta:
        abstract=True

class User_Message(Ticket_Message):
    ticket=models.ForeignKey(Ticket,on_delete=models.CASCADE,null=False,blank=False,related_name='messages',db_index=True,
                             verbose_name='تیکت مربوط به پیام',error_messages={'null':'تیکت مربوطه می بایست مشخص باشد'})


class Support_Response(Ticket_Message):
    parent_message=models.ForeignKey(User_Message,null=False,blank=False,db_index=True,related_name='responses',
                                     error_messages={'null':'این فیلد باید پر شود'},on_delete=models.CASCADE)
    is_read=models.BooleanField(default=False,verbose_name='آیا پاسخ توسط کاربر خوانده شده؟')