from django.db import models

# Create your models here.
class News(models.Model):
    title=models.CharField(max_length=300,verbose_name='عنوان خبر(حداکثر 300 کاراکتر)',null=False,blank=False)
    content=models.TextField(verbose_name='متن اصلی خبر')
    date=models.DateTimeField(verbose_name='تاریخ ایجاد خبر',auto_now_add=True)
    thumbnail=models.ImageField(upload_to='news_thumbs')
