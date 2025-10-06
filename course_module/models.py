from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from user_module.models import User,Teacher_Profile
from semester_module.models import Semester
# Create your models here.
class Class_Times(models.Model):
    days=(('شنبه','شنبه'),('یکشنبه','یکشنبه'),('دوشنبه','دوشنبه'),('سه شنبه','سه شنبه'),('چهارشنبه','چهارشنبه'),('پنج شنبه','پنج شنبه'))
    day=models.CharField(max_length=30,verbose_name='روز برگزاری',choices=days,default='شنبه')
    times=(('8-10','8-10')),(('10-12','10-12')),(('12-14','12-14')),(('14-16','14-16')),(('16-18','16-18')),(('18-20','18-20'))
    time=models.CharField(verbose_name='زمان برگزاری کلاس',choices=times,max_length=30)
    day_index=models.PositiveIntegerField(default=1)
    time_index=models.PositiveIntegerField(default=1)
    def save(self,*args,**kwargs):
        self.day_index=[x[0] for x in Class_Times.days].index(self.day)
        self.time_index=[x[0] for x in Class_Times.times].index(self.time)
        super().save(*args,**kwargs)




class Course(models.Model):
    teacher=models.ForeignKey(User,on_delete=models.CASCADE,null=False,blank=False,related_name='teacher_courses',db_index=True,verbose_name='استاد درس')
    students=models.ManyToManyField(User,related_name='attending_courses',db_index=True,verbose_name='دانشجویان درس',blank=True)
    credits=models.PositiveIntegerField(verbose_name='تعداد واحد درسی',validators=[MinValueValidator(1)])
    title=models.CharField(max_length=200,verbose_name='عنوان درس')
    course_types=(('نظری','نظری'),('آزمایشگاه','آزمایشگاه'),('عملی','عملی'),('کارگاه','کارگاه'),('پروژه','پروژه'),('پایان نامه','پایان نامه'),('رساله','رساله'))
    course_type=models.CharField(max_length=50,verbose_name='نوع درس',default='نظری')
    department_choices = (
    ('مهندسی', 'مهندسی'), ('علوم پایه', 'علوم پایه'), ('علوم انسانی', 'علوم انسانی'), ('علوم پزشکی', 'علوم پزشکی'),
    ('هنر', 'هنر'), ('تربیت بدنی', 'تربیت بدنی'))
    department = models.CharField(max_length=30, verbose_name='دانشکده محل برگزاری', choices=department_choices,
                                  null=False, blank=False,
                                  error_messages={'null': 'این فیلد باید مشخص شود'})
    area_code = models.CharField(max_length=20, verbose_name='کد محل برگزاری کلاس', null=False, blank=False,
                                 error_messages={'null': 'این فیلد باید مشخص شود'})
    degree_choices = (('کارشناسی پیوسته', 'کارشناسی پیوسته'), ('کارشناسی ناپیوسته', 'کارشناسی ناپیوسته'),
                      ('کاردانی پیوسته', 'کاردانی پیوسته')
                      , ('کاردانی ناپیوسته', 'کاردانی ناپیوسته'), ('کارشناسی ارشد ناپیوسته', 'کارشناسی ارشد ناپیوسته'),
                      ('دکتری حرفه ای', 'دکتری حرفه ای')
                      , ('دکتری مستقیم', 'دکتری مستقیم'), ('کارشناسی ارشد پیوسته', 'کارشناسی ارشد پیوسته'))
    for_degrees=models.CharField(max_length=30,verbose_name='این درس برای کدام مقطع تحصیلی می باشد',choices=degree_choices,default='کارشناسی پیوسته')
    capacity=models.IntegerField(verbose_name='ظرفیت کلاس')
    semester=models.ForeignKey(Semester,on_delete=models.CASCADE,null=False,blank=False,related_name='semester_courses',db_index=True,verbose_name='ترم تحصیلی مربوطه')
    class_times=models.ManyToManyField(Class_Times,related_name='classes',blank=True,verbose_name='زمان های برگزاری کلاس')
    requirements=models.ManyToManyField('Course',verbose_name='پیش نیاز ها',blank=True)
    exam_time=models.DateTimeField(verbose_name='زمان امتحان',null=True,blank=True)
    changes_history=models.JSONField(verbose_name='تاریخچه تغییرات درس',null=True,blank=True)
    def save(self,*args):
        super().save(*args)
    def __str__(self):
        return self.title
        
        
        
class Course_Score(models.Model):
    student=models.ForeignKey(User,on_delete=models.CASCADE,null=False,blank=False,related_name='scores',verbose_name='این نمره مربوط به کدام دانشجو می باشد')
    course=models.ForeignKey(Course,on_delete=models.CASCADE,null=False,blank=False,db_index=True,related_name='scores',verbose_name='نمره ربوط به کدام درس می باشد')
    score=models.FloatField(validators=[MinValueValidator(0),MaxValueValidator(20)],verbose_name='نمره دانشجو')
    class Meta:
        constraints=[models.UniqueConstraint(fields=['student','course'],name='check score uniquness',violation_error_message='رکورد نمره این دانشجو برای این درس قبلا ایجاد شده است')]
    def save(self,*args):
        if not (self.student in self.course.students.all()):
            raise ValidationError('این کاربر جزو دانشجویان این درس نمی باشد!')
        super().save(*args)
        self.student.student_profile.update_average()

    def __str__(self):
        return f'course {self.course.title}  student {self.student} score {self.score}'


class Score_Appeal(models.Model):
    score=models.OneToOneField(Course_Score,on_delete=models.CASCADE,verbose_name='این اعتراض برای کدام نمره نوشته شده است'
                               ,null=False,blank=False,related_name='appeal',error_messages={'null':'این فیلد نمی تواند خالی باشد'})
    text=models.TextField(verbose_name='متن اعتراض')
    date=models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ثبت اعتراض')

