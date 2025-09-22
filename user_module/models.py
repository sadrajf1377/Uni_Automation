from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Avg, ExpressionWrapper, F, FloatField, Sum, Count


# Create your models here.
def phone_validator(input: str):
    if not input.isnumeric() or len(input) != 11:
        raise ValidationError('شماره تلفن باید 11 رقم باشد و کاراکتر غیر عددی نداشته باشه')

def nat_number_validator(input):
    if not input.isnumeric() or len(input)!=10:
        raise ValidationError('شماره ملی باید 10 رقم باشد و کاراکتر غیر عددی نداشته باشه')
class User(AbstractUser):
    phone_number = models.CharField(max_length=11, verbose_name='شماره تلفن', validators=[phone_validator],
                                    null=False, blank=False,
                                    error_messages={'null': 'شماره تلفن کاربر باید وارد شود'})
    national_number = models.CharField(max_length=10, verbose_name='شماره ملی کاربر (ضروری)', null=False, blank=False,
                                       error_messages={'null': 'شماره ملی کاربر باید وارد شود','unique':'کاربری با این شماره ملی قبلا ثبت نام کرده است'},
                                       unique=True,validators=[nat_number_validator])
    date_joined = models.DateField(auto_now_add=True, verbose_name='زمان ساخت حساب کاربری')
    u_types=(('دانشجو','دانشجو'),('استاد','استاد'),('کارمند یا کارشناس','کارمند یا کارشناس'))

    user_type=models.CharField(choices=u_types,max_length=20,verbose_name='نوع کاربر',default='دانشجو',null=False,blank=False,error_messages={'null':'نوع کاربر باید مشخص باشد'})

    def save(self, *args, **kwargs):
        if self.id == None:
            self.system_number = str(self.date_joined) + self.national_number[:4:]
        super().save(*args, **kwargs)

class General_Profile(models.Model):
    avatar = models.ImageField(upload_to='avatars',null=True,blank=True,verbose_name='تصویر کاربر')
    area_code = models.CharField(max_length=20, verbose_name='کد محل فعالیت', null=False, blank=False,error_messages={'null':'این فیلد باید مشخص شود'})
    sex = models.CharField(verbose_name='جنسیت', max_length=20,
                           choices=(('مرد', 'مرد'), ('زن', 'زن'), ('نامشخص', 'نامشخص')), null=False, blank=False,error_messages={'null':'این فیلد باید مشخص شود'})
    degree_choices = (('کارشناسی پیوسته', 'کارشناسی پیوسته'), ('کارشناسی ناپیوسته', 'کارشناسی ناپیوسته'),
                      ('کاردانی پیوسته', 'کاردانی پیوسته')
                      , ('کاردانی ناپیوسته', 'کاردانی ناپیوسته'), ('کارشناسی ارشد ناپیوسته', 'کارشناسی ارشد ناپیوسته'),
                      ('دکتری حرفه ای', 'دکتری حرفه ای')
                      , ('دکتری مستقیم', 'دکتری مستقیم'), ('کارشناسی ارشد پیوسته', 'کارشناسی ارشد پیوسته'))
    latest_degree=models.CharField(max_length=30,verbose_name=' آخرین مقطع تحصیلی',choices=degree_choices,null=False,blank=False,error_messages={'null':'این فیلد باید مشخص شود'})

    latest_certificate_picture = models.ImageField(upload_to='students_certs',
                                                   verbose_name='تصویر مدرک آخرین مقطع تحصیلی ',null=False,blank=False,error_messages={'null':'این فیلد باید مشخص شود'})
    latest_degree_code=models.CharField(max_length=25,verbose_name='کد رشته آخرین مقطع تحصیلی',null=False,blank=False,error_messages={'null':'این فیلد باید مشخص شود'})
    department_choices=(('مهندسی','مهندسی'),('علوم پایه','علوم پایه'),('علوم انسانی','علوم انسانی'),('علوم پزشکی','علوم پزشکی'),('هنر','هنر'),('تربیت بدنی','تربیت بدنی'))
    department=models.CharField(max_length=30,verbose_name='دانشکده محل فعالیت',choices=department_choices,null=False,blank=False,
                                error_messages={'null':'این فیلد باید مشخص شود'})
    is_approved=models.BooleanField(verbose_name='آیا این پروفایل تایید شده است یا خیر؟',default=False)
    approval_document=models.ImageField(upload_to='profile_approvals',null=True,blank=True,verbose_name='اسکن مدرک تایید پروفایل')
    def save(self,*args):
        if self.is_approved and self.approval_document==None:
            raise ValidationError(' تایید وضعیت کاربر بدون بارگزاری تصویر اسکن مدرک تایید ممکن نمی باشد!')
        super().save(*args)
    class Meta:
        abstract=True





class Student_Profile(General_Profile):
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=False,blank=False,related_name='student_profile',error_messages={'null':'کاربر مربوطه باید مشخص بشود'})
    student_number=models.TextField()
    average=models.FloatField(verbose_name='معدل دانشجو',null=True,blank=True)

    degree=models.CharField(choices=General_Profile.degree_choices,verbose_name=' مقطع تحصیلی فعلی',null=False,blank=False,max_length=40,error_messages={'null':'این فیلد باید مشخص شود'})
    status_choices=(('عادی','عادی'),('اخراج','اخراج'),('مرخصی','مرخصی'),('فارغ التحصیل','فارغ التحصیل'))
    status=models.CharField(choices=status_choices,default='عادی',max_length=40,verbose_name='وضعیت دانشجو',null=False,blank=False,error_messages={'null':'این فیلد باید مشخص شود'})
    current_degree_code = models.CharField(max_length=25, verbose_name='کد رشته  مقطع تحصیلی فعلی', null=False,
                                          blank=False,error_messages={'null':'این فیلد باید مشخص شود'})

    def save(self,*args):
        user=self.user
        if user.user_type!='دانشجو':
            raise ValidationError('کاربر مورد نظر دانشجو نمی باشد')
        if self.id==None:
             self.student_number=f'{user.date_joined.year}{user.national_number[:5]}'


        super().save(*args)
    class Meta:
        indexes=[models.Index(fields=['department','degree','current_degree_code'],name=' index for studetns')]
    def update_average(self):
        total=self.user.scores.all().select_related('course').aggregate(
            sum=Sum(ExpressionWrapper(F('score')*F('course__credits'),output_field=FloatField())),
        count=Sum('course__credits'))
        self.average=total['sum']/total['count']
        print(total)
        super().save()

class Teacher_Profile(General_Profile):
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=False,blank=False,related_name='teacher_profile',verbose_name='این اطلاعات مربوط به کدام استاد می باشد',error_messages={'null':'این فیلد باید مشخص شود'})
    rank_choices=(('استادیار','استادیار'),('دانشیار','دانشیار'),('استاد تمام','استاد تمام'))
    rank=models.CharField(max_length=30,verbose_name='مرتبه علمی استاد',choices=rank_choices,null=False,blank=False,
                          error_messages={'null':'مرتبه علمی استاد باید مشخص شود'})
    role_choices=(('مدیر گروه','مدیر گروه'),('مسوول پژوهشی','مسوول پژوهشی'),('رییس دانشکده','رییس دانشکده'),('عادی','عادی'))
    role=models.CharField(max_length=25,verbose_name='نقش استاد',choices=role_choices,default='عادی')
    is_faculty=models.BooleanField(verbose_name='آیا استاد مربوطه عضو هیت علمی می باشد؟',default=False)
    def save(self,*args):
        teacher_role=self.role
        if teacher_role == 'مدیر گروه' or teacher_role == 'رییس دانشکده':
            if Teacher_Profile.objects.filter(~Q(user_id=self.user_id),role=teacher_role,latest_degree=self.latest_degree,department=self.department).exists():
                raise ValidationError(f'نقش {teacher_role} در این مجتمع قبلا برای استاد دیگری تعریف شده است')
        if self.user.user_type!='استاد':
            raise ValidationError('کاربر مربوط به این پروفایل بایستی استاد باشد')
        super().save(*args)
    class Meta:
        indexes=[models.Index(fields=['department','rank','latest_degree_code'],name='index combo for teachers')]
                

class Employee_Profile(General_Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False, related_name='employee_profile',
                                verbose_name='این اطلاعات مربوط به کدام کارمند می باشد',
                                error_messages={'null': 'این فیلد باید مشخص شود'})
    role_choices=(('کارشناس آموزش','کارشناس آموزش'),('کارشناس گروه','کارشناس گروه'))
    role=models.CharField(max_length=30,verbose_name='نقش کارمند',default='عادی',choices=role_choices)

    class Meta:
        indexes = [models.Index(fields=['role', 'latest_degree_code'], name='index combo for employees')]
    def save(self,*args):
        if self.user.user_type!='کارمند یا کارشناس':
            raise ValidationError(f'کاربر مربوط به این پروفایل باید از نوع کارمند یا کارشناس باشد')
        super().save(*args)







# Create your models here.
