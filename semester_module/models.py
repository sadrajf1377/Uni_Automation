from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Count, When, Value, Case, F, ExpressionWrapper, BooleanField, IntegerField
from user_module.models import User,Student_Profile
degrees_max_semesters={'کارشناسی پیوسته': 10, 'کارشناسی ناپیوسته': 6,
                      'کاردانی پیوسته': 4,
                       'کاردانی ناپیوسته': 4, 'کارشناسی ارشد ناپیوسته':6,
                      'دکتری حرفه ای': 16
                      , 'دکتری مستقیم': 16, 'کارشناسی ارشد پیوسته': 16}


class Current_Semester(models.Model):
    semester=models.ForeignKey('Semester',on_delete=models.CASCADE,null=False,blank=False)
    def save(self,*args):
        cond=Current_Semester.objects.exists()
        if cond:
            initial = Current_Semester.objects.all()[0].semester or None
            if self.semester != initial and initial.semester_status != 'بسته':
                raise ValidationError('امکان تغییر ترم فعلی تا به پایان نرسیدن آن وجود ندارد!')
            if Current_Semester.objects.exclude(id=self.id).exists():
                raise ValidationError('تنها یک نمونه از ترم فعلی می تواند وجود داشته باشه')
        super().save(*args)



# Create your models here.
class Semester(models.Model):
    start_date=models.DateField(verbose_name='زمان شروع ترم')
    end_date=models.DateField(verbose_name='زمان پایان ترم')
    sem_types=(('تابستان','تابستان'),('عادی','عادی'))
    semester_type=models.CharField(max_length=30,choices=sem_types,default='عادی',verbose_name='نوع ترم')
    status_choices=(('شروع نشده','شروع نشده'),('انتخاب واحد','انتخاب واحد'),('جاری','جاری'),('امتحان','امتحان'),('بسته','بسته'))
    semester_status=models.CharField(verbose_name='وضعیت ترم',choices=status_choices,max_length=40,default='شروع نشده')
    def save(self,*args):
        start=self.start_date
        end=self.end_date
        if self.end_date<self.start_date or Semester.objects.exclude(id=self.id).filter(Q(end_date__gte=start,start_date__lte=end)).exists():
            raise ValidationError(' زمان پایان ترم نمی تواند زود تر از شروع آن باشد و شروع هیچ ترمی نباید پیش از پایان ترم دیگری باشد')
        if Semester.objects.filter(semester_status='جاری'):
            raise ValidationError('امکان تعریف ترم جدید تا تمام نشدن ترم جاری وجود ندارد!')
        first_time=self.id==None
        super().save(*args)
        if first_time:
            annotate_cap = [When(degree=key, then=Value(val)) for key, val in
                            degrees_max_semesters.items()]
            Student_Profile.objects.filter(is_approved=True).select_related('user').annotate(max_cap=Case(*annotate_cap,output_field=IntegerField()),
                            semesters_passed=Count('user__attending_courses__semester',distinct=True)).annotate(sems_left=ExpressionWrapper(
                -F('semesters_passed')+F('max_cap'),output_field=IntegerField()
            )).filter(sems_left__lte=0).update(status='اخراج')


    def duration(self):
        return (self.end_date-self.start_date).seconds
    def __str__(self):
        return f'start date :{self.start_date}  end date:{self.end_date}'