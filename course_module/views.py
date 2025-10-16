import json

import redis
from django.db import IntegrityError
from django.db.models import OuterRef, Prefetch, Subquery, Avg, ExpressionWrapper, F, FloatField, Q, Sum, IntegerField, \
    Case, When, Value, CharField, Count, Window, Exists
from django.db.models.functions import Rank
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, CreateView

from semester_module.models import Semester
from user_module.models import User,General_Profile
from .models import Course,Course_Score,Class_Times,Score_Appeal
from semester_module.models import Current_Semester
from .forms import Course_Filter_Form,Appeal_Form
from utils.decorators import restrict_view_access
from utils.decorators import check_semester_status
from exam_module.models import Exam
# Create your views here.
##this section belongs to students views

from django.core.cache import caches
class View_Courses_Reports(ListView):
    template_name = 'Scores_Report.html'
    model = Semester
    context_object_name = 'semesters'
    ordering = 'start_date'
    def dispatch(self, request, *args, **kwargs):
        self.average=-1
        return super().dispatch(request=request)
    def get_queryset(self):
        user=self.request.user
        score_subquery=Course_Score.objects.filter(student_id=user.id,course_id=OuterRef('pk')).values('score')[:1:]
        appeal_text=Score_Appeal.objects.select_related('score').filter(score__student=user,score__course_id=OuterRef('pk')).values_list('text',flat=True)[:1:]
        pass_status=Case(When(score__gte=10,then=Value('قبول')),When(score__lt=10,then=Value('مردود')),output_field=CharField())
        semesters=Semester.objects.filter(semester_courses__students=user).prefetch_related(
            Prefetch('semester_courses',queryset=Course.objects.prefetch_related('scores').filter(
                students=user).annotate(score=Subquery(score_subquery)).annotate(pass_status=pass_status,appeal_text=Subquery(appeal_text)),
                     to_attr='sem_courses')
        ).annotate(total_scores=Sum(ExpressionWrapper(F('semester_courses__scores__score')*F('semester_courses__credits'),output_field=FloatField())
                                    ,filter=Q(semester_courses__scores__student=user)
                                    ),
                   ).annotate(total_credits=Sum('semester_courses__credits',filter=Q(semester_courses__scores__student=user)))\
            .annotate(sem_average=ExpressionWrapper(F('total_scores')/F('total_credits'),output_field=FloatField()))

        st=semesters.aggregate(total_avg=Sum('sem_average'),total_count=Count('id'))
        print('st',st)
        self.average=st['total_avg'] if st['total_avg'] else 1/(st['total_count'] if st['total_count'] else -1)
        return semesters
    def get_context_data(self, *, object_list=None, **kwargs):
        context=super().get_context_data(**kwargs)
        context['total_average']=self.average
        return context


class Total_Report_Card(View_Courses_Reports):
    pass


class View_Semester_Report(View_Courses_Reports):
    def get_context_data(self, *, object_list=None, **kwargs):
        context=super().get_context_data()
        context['appeal_form']=Appeal_Form()
        return context
    def get_queryset(self):
        current_semester=self.request.session.get('semester') or Current_Semester.objects.all()[0].id
        has_appeal=Score_Appeal.objects.select_related('score').filter(score__course_id=OuterRef('pk'))
        query=super().get_queryset().filter(id=current_semester).annotate(has_appeal=Exists(has_appeal))
        return query


class My_Schedule(View):
    def get(self,request):
        user=request.user
        current_semester_id=request.session.get('semester') or Current_Semester.objects.all()[0].id
        query=list(Class_Times.objects.prefetch_related(Prefetch('classes',queryset=Course.objects.filter(
            students=user,semester_id=current_semester_id),to_attr='day_classes')).order_by('day_index'))
        days=[x[0] for x in Class_Times.days]
        times=[x[0] for x in Class_Times.times]
        result={}
        starting_index=0


        for day in days:
            matching_objs=[x for x in query if any(x.day_classes) and x.day==day][starting_index::]
            starting_index+=len(matching_objs)-1
            ordered=[]
            for time in times:
                obj=next((x for x in matching_objs if x.time==time),None)
                ordered.append('\n'.join([x.title for x in obj.day_classes]) if obj else '---')
            result[day]=ordered


        return render(request,'Weekly_Schedule.html',context={'days':result})


class Create_Course(CreateView):
    template_name = 'General_Form.html'
    model = Course
    fields = ['credits','course_type','department','area_code','for_degrees','capacity','class_times']
    success_url = reverse_lazy('index')
    def get_object(self, queryset=None):
        obj=super().get_object()
        obj.semester=Current_Semester.objects.all()[0]
        return obj

@method_decorator(check_semester_status(status_permits_pair={'انتخاب واحد':'','جاری':'انتخاب واحد خارج از بازه'},response_type='html'),name='dispatch')
class Current_Semester_Courses(ListView):
    template_name = 'Courses_List.html'
    model = Course
    context_object_name = 'courses'
    paginate_by = 20
    def get_queryset(self):
        parameters=self.kwargs
        condition=Q()
        if parameters['title']!='all':
            condition &=Q(title__contains=parameters['title'])
        if parameters['department']!='all':
            condition &=Q(department=parameters['department'])
        if parameters['degree']!='all':
            condition&=Q(for_degrees=parameters['degree'])
        if parameters['course_type']!='all':
            condition&=Q(course_type=parameters['course_type'])
        sem_id=self.request.session.get('semester') or Current_Semester.objects.first().semester.id
        query=super().get_queryset().filter(condition,semester_id=sem_id).prefetch_related('students').annotate(std_count=Count('students')).annotate(cap_left=
                                                ExpressionWrapper(F('capacity')-F('std_count'),output_field=IntegerField()))
        return query
    def get_context_data(self, *, object_list=None, **kwargs):
        context=super().get_context_data()
        context['search_form']=Course_Filter_Form()
        red=redis.StrictRedis.from_url(url='redis://redis:6379/1')
        
        user_sem_data=json.loads(red.hget('students_stats',self.request.user.id))
        context['stats']=user_sem_data
        sem = self.request.session.get('semester')
        sem = sem if sem != None else Current_Semester.objects.first().semester.id
        context['student_courses']=Course.objects.filter(semester_id=sem,students=self.request.user)
        return context

@method_decorator(restrict_view_access(profile_types=['teacher']),name='dispatch')
class Teacher_Courses(ListView):
    template_name = 'Teacher_Courses.html'
    model = Course
    context_object_name = 'courses'
    paginate_by = 20
    ordering = '?'
    def get_queryset(self):
        user=self.request.user
        has_exam=Exam.objects.filter(course_id=OuterRef('pk'))
        current_sem_id=self.request.session.get('semester') or Current_Semester.objects.all()[0].id
        query=user.teacher_courses.all().filter(semester_id=current_sem_id).prefetch_related('students').annotate(scores_average=Avg('students__scores',filter=Q(students__scores__course_id=F('pk')))
        ,students_count=Count('students')
                                                                                                                  ,has_exam=Exists(has_exam)).prefetch_related(Prefetch('class_times',queryset=Class_Times.objects.all(),to_attr='times'))
        print(query)
        return query

@method_decorator(restrict_view_access(profile_types=['teacher']),name='dispatch')
class Course_Details(ListView):
    template_name = 'Course_Details.html'
    context_object_name = 'students'
    model=User
    def dispatch(self, request, *args, **kwargs):
        course_id = self.kwargs['course_id']
        self.course=get_object_or_404(Course,id=course_id,teacher=self.request.user)
        return super().dispatch(request)
    def get_queryset(self):
        course_id=self.kwargs['course_id']
        score_sub=Course_Score.objects.filter(student_id=OuterRef('pk'),course_id=course_id).values('score')[:1:]
        query=self.course.students.all().annotate(score=Subquery(score_sub))
        return query
    def get_context_data(self, *, object_list=None, **kwargs):
        context=super().get_context_data()
        context['course']=self.course
        return context

@method_decorator(restrict_view_access(profile_types=['teacher']),name='dispatch')
class Update_Courses_Details(View):
    def post(self,request:HttpRequest,course_id):

        try:
            course = get_object_or_404(Course, id=course_id, teacher=request.user)
            data = json.loads(request.body.decode('utf-8'))
            students_to_delete =data.get('students_to_delete')
            scores_to_update ={int(key):float(value) for key,value in  data.get('scores_to_update').items()}
            scores = course.scores.all().filter(student_id__in=scores_to_update.keys()).select_for_update()
            to_update = []
            print(scores_to_update)
            for sc in scores:
                sc.score = scores_to_update.get(sc.student_id)
                to_update.append(sc)
            course.scores.bulk_update(to_update, fields=['score'])
            for std in course.students.filter(id__in=students_to_delete):
                course.students.remove(std)
            return redirect(reverse('view_course_details', args=[course_id]))
        except Course.DoesNotExist:
            return render(request,'Dynamic_Message.html',context={'message':'درسی با مشخصات ذکر شده یافت نشد'},status=404)
        except Exception as e:

            print('exception',e)
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجدد تلاش بفرمایید'},status=500)


class Delete_Course_Students(View):
    def post(self,request,course_id):
        data=json.loads(request.body)
        ids=data['students_ids']
        course=get_object_or_404(Course,id=course_id,teacher=request.user)
        students=course.students.filter(id_in=data['students_ids'])
        if len(students)!=ids:
            return JsonResponse(data={'message':'برخی از دانشجو های مشخص شده در لیست دانشجویان این درس نیستند!'})
        course.students.remove(students)
        course.changes_history['students_removed']=students.values_list('username',flat=True)
        course.save()
        return JsonResponse(data={'message':'دانشجویان با موفقیت حذف شدند!'})


class Submite_Students_Scores(View):
    def get(self,request,course_id):
        try:
            course=request.user.teacher_courses.get(id=course_id)
            score=Course_Score.objects.filter(student_id=OuterRef('pk'),course_id=course_id).values_list('score',flat=True)[:1:]
            students=course.students.all().annotate(score=Subquery(score))
            return render(request,'Course_Details.html',context={'students':students},status=200)
        except:
            pass
    def post(self,request,course_id):
        try:
            data = json.loads(request.body)
            students_scores = data['students_scores']
            course = request.user.teacher_courses.get(id=course_id)
            scores = course.scores.filter(student_id__in=students_scores.keys())
            if len(scores) != len(students_scores.keys()):
                return JsonResponse(data={'message': 'تعدادی از دانشجویان وارد شده یافت نشدند'}, status=401)
            scores_to_update = []
            for sc in scores:
                sc.score = students_scores[sc.student_id]
                students_scores.append(sc)
            Course_Score.objects.bulk_update(scores_to_update, fields=['score'])
            return JsonResponse(data={'message': 'نمرات با موفقیت تغییر کردند'},status=201)
        except Course.DoesNotExist:
            return JsonResponse(data={'message':'درسی با مشخصات وارد شده یافت نشد'},status=404)
        except KeyError:
            return JsonResponse(data={'message':'داده به صورت صحیح وارد نشده است!'},status=402)
        except:
            return JsonResponse(data={'message':'مشکلی در پردازش درخواست به وجود آمد!لطفا مجدد تلاش بفرمایید!'},status=500)


@method_decorator(check_semester_status(status_permits_pair={'انتخاب واحد':'انتخاب واحد','جاری':'انتخاب واحد خارج از بازه'},response_type='html'),name='dispatch')
class Pick_Courses(View):
    def post(self,request,course_id):
        red=redis.StrictRedis.from_url(url='redis://redis:6379/1')
        stats=json.loads(red.hget('students_stats',request.user.id))
        print(stats)
        initial_stats=stats
        if stats==None or stats=={}:
            return render(request,'Dynamic_Message.html',context={'message':'شما مجاز به انجام عملیات انتخاب واحد نمی باشید!'},status=401)
        try:
            course = get_object_or_404(Course, id=course_id)
            creds_check = 'سقف دروس ترم رعایت نشده است' if not stats['sem_creds'] + course.credits <= stats[
                'max_cap'] else ''
            passed_courses = stats['passed_courses']
            requirements = course.requirements.all().values_list('title', flat=True)
            requirements_check = 'پیشنیاز های درس رعایت نشده است' if not (passed_courses=='__all__') and (any(
                [x for x in requirements if not x in passed_courses])) else ''
            course_times = course.class_times.all().values_list('id', flat=True)
            check_times = 'ساعت کلاس ها تداخل دارد' if any(
                [x for x in course_times if x in stats['class_times']]) else ''
            if not any([x for x in [requirements_check, check_times, creds_check] if x != '']):
                course.students.add(request.user)
                stats['sem_creds'] += course.credits
                stats['class_times'].extend(course.class_times.values_list('id', flat=True))

                red.hset('students_stats',request.user.id, json.dumps(stats))
                return JsonResponse(data={'message': 'درس با موفقیت اضافه شد!'}, status=201)
            else:
                return JsonResponse(data={'message': 'مشکلی در انتخاب درس به وجود آمد!',
                                          'errors': '\n'.join(
                                              [x for x in [check_times, creds_check, requirements_check] if x != ''])},
                                    status=401)
        except Exception as e:
            course.students.remove(request.user)
            red.hset('students_stats',request.user.id,json.dumps(initial_stats))

            return JsonResponse(data={'message':'مشکلی در ثبت درس به وجود آمد!لطفا مجدد تلاش بفرمایید!','errors':str(e),'s':initial_stats},status=500)



@method_decorator(check_semester_status(status_permits_pair={'انتخاب واحد':'انتخاب واحد','جاری':'انتخاب واحد خارج از بازه'},response_type='html'),name='dispatch')
class Delete_Course(View):
    def post(self,request,course_id):
        initial_stats=''
        try:
           course=Course.objects.get(id=course_id,students=request.user)
           red=redis.StrictRedis.from_url('redis://redis:6379/1')
           st=red.hget('students_stats',request.user.id)
           initial_stats=st
           stat=json.loads(st)
           for id in course.class_times.all().values_list('id',flat=True):
               stat['class_times'].remove(id)
           stat['sem_creds'] -= course.credits
           red.hset('students_stats',request.user.id,json.dumps(stat))
           course.students.remove(request.user)
           return JsonResponse(data={'message':'درس با موفقیت حذف شد'},status=201)
        except Course.DoesNotExist:
            return JsonResponse(data={'message':'درس مورد نظر یافت نشد'},status=404)
        except:
            if initial_stats!='':
                red.hset('students_stats',request.user.id,json.dumps(initial_stats))
                course.students.add(request.user)
            return JsonResponse(data={'message':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجدد تلاش بفرمایید'},status=500)


@method_decorator(check_semester_status(status_permits_pair={'امتحان':'__all__'},response_type='html'),name='dispatch')
class Student_Exams(ListView):
    template_name = 'Exams_Schedule.html'
    model=Course
    context_object_name = 'courses'
    ordering = '-exam_time'
    def dispatch(self, request, *args, **kwargs):
        self.sem=Semester.objects.get(id=self.request.session.get('semester')) or Current_Semester.objects.first().semester
        review_sessions=self.request.user.student_reviews.filter(semester=self.sem)
        cond=any([x for x in review_sessions if x.session_closed==False]) or not any(review_sessions)
        if cond:
            return render(request,'Dynamic_Message.html',context={'message':'برای مشاهده برنامه امتحانات می بایستی ارزشیابی تمامی اساتید ان ترم را انجام دهید!'})
        return super().dispatch(request=request,*args,**kwargs)
    def get_queryset(self):
        sem=self.sem
        query=Course.objects.filter(semester=sem,students=self.request.user)
        return query



class Top_Students(View):
    def get(self,request):
        query=list(User.objects.filter(user_type='دانشجو').select_related('student_profile').prefetch_related('scores').annotate(
            dep=F('student_profile__department'),avg=Sum(F('scores__score')*F('scores__course__credits'))/Sum('scores__course__credits')).annotate(
            dep_rank=Window(expression=Rank(),partition_by=F('dep'),order_by=F('avg').desc())
        ).filter(dep_rank__lte=3))
        deps=[x[0] for x in General_Profile.department_choices]
        result={dep:[x for x in query if x.dep==dep] for dep in deps}
        print(result)
        return JsonResponse(data={})


@method_decorator(restrict_view_access(profile_types=['student']),name='dispatch')
class Submit_Score_Appeal(View):
    def post(self,request,course_id):
        try:
            score=request.user.scores.get(course_id=course_id)
            frm=Appeal_Form(data=request.POST)
            if frm.is_valid():
                frm.instance.score=score
                frm.save()
                return JsonResponse(data={'message':'اعتراض با موفقیت ثبت شد!'},status=201)
            else:
                errors='\n'.join([x for x in frm.errors])
                return JsonResponse(data={'message':'مشکلی در ثبت اعتراض به وجود آمد!لطفا مجددا تلاش بفرمایید!','errros':errors},status=401)
        except Course_Score.DoesNotExist:
            return JsonResponse(data={'message':'نمره ای برای ثبت اعتراض پیدا نشد'},status=404)
        except IntegrityError as e:
            print(e)
            return JsonResponse(data={'message':'مشکلی در پردازش شاما به وجود آمد!لطفا مجددا تلاش بفرمایید!'},status=500)
