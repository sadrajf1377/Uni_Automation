import redis
from django.db import transaction
from django.db.models import Window, F, Sum, OuterRef, Subquery, ExpressionWrapper, FloatField
from django.db.models.functions import Lag
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

from user_module.models import User
from .models import Permit
from semester_module.models import Current_Semester
from .forms import Permit_Form

from semester_module.models import Semester,Current_Semester
from course_module.models import Course_Score,Course
import redis as red
import json
# Create your views here.
def max_credits(degree,avg):
    max_cap=6
    if degree.__contains__('کارشناسی'):
        if degree.__contains__('ارشد'):
            print('arashad')
            if avg < 14:
                max_cap = 8
            elif avg > 14:
                max_cap = 16 if avg >= 17 else 14
        else:
            print('karshenasi55')
            if avg < 12:
                max_cap = 14
            elif avg > 14:
                max_cap = 24 if avg >= 17 else 20
    elif degree.__contains__('کاردانی'):
        print('kardani')
        if avg < 10:
            max_cap = 8
        elif avg > 10:
            max_cap = 20 if avg >= 16 else 16
    elif degree.__contains__('دکتری'):
        print('doctori')
        if avg < 17:
            max_cap = 6
        elif avg > 14:
            max_cap = 16 if avg >= 18 else 12
    else:
        if avg < 14:
            max_cap = 8
        elif avg > 14:
            max_cap = 16 if avg >= 17 else 14
    print(max_cap)
    return max_cap

def generate_student_stats(user,sem_id):
    redis = red.StrictRedis.from_url(url='redis://redis:6379/1')
    degree = user.student_profile.degree
    objs = Semester.objects.all().annotate(
        prev=Window(expression=Lag('id'), order_by=F('start_date').asc()))
    previous_sem_id = next((x.prev for x in objs if x.id == sem_id), None)
    user_scores = user.scores.all().select_related('course')
    prev_sem_stats = user_scores.filter(course__semester_id=previous_sem_id).annotate(
        total=ExpressionWrapper(F('score') * F('course__credits'),
                                output_field=FloatField())) \
        .aggregate(total_credits=Sum('course__credits'), total_scores=Sum('total'))
    total_scores = prev_sem_stats['total_scores']
    total_creds = prev_sem_stats['total_credits']

    if total_creds == None:
        max_cap = 20
    else:
        avg = total_scores / total_creds
        max_cap = max_credits(degree, avg)
        print(max_cap)

    passed_courses = list(
        set(user_scores.filter(score__gte=10).values_list('course__title', flat=True)))
    j = json.dumps(
        {'max_cap': max_cap, 'passed_courses': passed_courses, 'class_times': [], 'sem_creds': 0})
    redis.hset('students_stats', user.id,j)


class Permits_List(ListView):
    template_name = 'Permits.html'
    model = Permit
    context_object_name = 'permits'
    def get_queryset(self):
        sem_id=self.request.session.get('semester') or Current_Semester.objects.first().semester.id
        query=self.request.user.permits.all().filter(semester_id=sem_id)
        return query

class Ask_For_Permit(View):
    def get(self,request):
        frm=Permit_Form(initial={'semester':Current_Semester.objects.first().semester.id})
        return render(request,'General_Form.html',context={'form':frm,'url_name':'ask_for_permit'})
    def post(self,request):
        frm=Permit_Form(request.POST)
        user:User=request.user
        print('called')
        if frm.is_valid():
            try:
                with transaction.atomic():
                    inst=frm.instance
                    inst.creator=user
                    inst.save()
                    if inst.permite_type=='انتخاب واحد':
                        generate_student_stats(user,inst.semester.id)
                    return render(request,'Dynamic_Message.html',{'message':'درخواست انتخاب واحد شما با موفقیت ثبت شد'},status=201)


            except Exception as e:
                frm.add_error('permit_type',str(e))
                try:
                  redis = red.StrictRedis.from_url(url='redis://redis:6379/1')
                  redis.hdel('students_stats', user.id)
                except:
                    pass

                return render(request, 'General_Form.html', context={'form': frm, 'url_name': 'ask_for_permit'},status=500)
        else:
            return render(request, 'General_Form.html', context={'form': frm, 'url_name': 'ask_for_permit'},status=401)


class UnConfirmed_Permits(ListView):
    template_name = 'Permits_To_Confirm.html'
    model = Permit
    context_object_name = 'permits'
    paginate_by = 20
    ordering = '-date'
    def get_queryset(self):
        em_prof=self.request.user.employee_profile
        area_code=em_prof.area_code
        dep=em_prof.department
        query=super().get_queryset().select_related('creator').filter(is_confirmed=False,creator__student_profile__area_code=area_code,
                                                                                       creator__student_profile__department=dep).annotate(creator_name=F('creator__username'))\
            .values('creator_name','date','permit_type')
        return query


class Confirm_Permit(View):
    def post(self,request):
        try:
            permit_id=request.POST.get('permit_id')
            user_prof=request.user.employee_profile
            permit=Permit.objects.select_related('creator').get(id=permit_id,creator__student_profile__area_code=user_prof.area_code,creator__student_profile__department=user_prof.department)
            p_type=permit.permit_type
            if p_type=='انتخاب واحد خارج از بازه':
                generate_student_stats(permit.creator,permit.semester.id)
            elif p_type=='ترم آخری':
                red=redis.StrictRedis('redis://redis:6379/1')
                student_data=json.dumps({'max_cap':24,'passed_courses':'__all__', 'class_times': [], 'sem_creds': 0})
                red.hset('students_stats',permit.creator.id,student_data)
            permit.is_confirmed=True
            permit.save()
            return JsonResponse(data={'message':'مجوز با موفقیت تایید شد!'},status=201)
        except Exception as e:
            try:
                red=redis.StrictRedis('redis://redis:6379/1')
                red.hdel('students_stats',permit.creator.id)
            except:
                pass
            permit.is_confirmed=False
            permit.save()
            if isinstance(e,Permit.DoesNotExist):
               return JsonResponse(data={'message':'مجوزی با مشخصات داده شده یافت نشد!'},status=404)
            elif isinstance(e,KeyError):
                return JsonResponse(data={'message':'داده های مورد نیاز به درستی وارد نشده اند'},status=409)
            else:
                return JsonResponse(data={'message':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجددا تلاش بفرمایید!'},status=500)


