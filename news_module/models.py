from django.core.exceptions import ValidationError
from django.db import models
from user_module.models import User
# Create your models here.




class News(models.Model):
    title=models.CharField(max_length=300,verbose_name='عنوان خبر(حداکثر 300 کاراکتر)',null=False,blank=False)
    content=models.TextField(verbose_name='متن اصلی خبر')
    date=models.DateTimeField(verbose_name='تاریخ ایجاد خبر',auto_now_add=True)
    is_archived=models.BooleanField(verbose_name='آیا خبر آرشیو شده است؟',default=False)
    author=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='published_news')



class News_Images(models.Model):
    image=models.ImageField(upload_to='news_images',verbose_name='تصویر خبر')
    news=models.ForeignKey(News,on_delete=models.CASCADE,null=False,blank=False,related_name='images',db_index=True)
    def clean(self):
        if self.image.size > 1500000:
            raise ValidationError('اندازه فایل تصویر باید کمتر از 1.5 مگابایت باشد')
        super().clean()


