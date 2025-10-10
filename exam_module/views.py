import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import OuterRef, Exists, F, ExpressionWrapper, DecimalField, DateTimeField, DateField, TimeField, \
    FloatField, Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from .models import Exam,Exam_Answer
from .forms import Exam_Form,Exam_Answer_Form
from course_module.models import Course
from semester_module.models import Current_Semester
from zoneinfo import ZoneInfo
# Create your views here.
class Create_Exam(View):
    def get(self,request,course_id):
        try:
           course=request.user.teacher_courses.all().get(id=course_id)
           frm=Exam_Form()
           return render(request,'Update_&_Create_Exam.html',context={'form':frm,'to_do':'create','course_name':course.title,'course_id':course.id},status=200)
        except Course.DoesNotExist:
            return render(request,'Dynamic_Message.html',context={'message':'درسی با مشخصات وارد شده یافت نشد'},status=404)
        except Exception as e:
            print(e)
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد!'},status=500)

    def post(self, request,course_id):

        try:
                course=Course.objects.get(id=course_id,teacher=request.user)
                frm = Exam_Form(request.POST)
                if frm.is_valid():
                    frm.instance.course=course
                    frm.save()
                    return redirect(reverse('teacher_courses'))
                else:
                    return render(request,'Update_&_Create_Exam.html',context={'form':frm,'to_do':'create','course_name':course.title,'course_id':course.id},status=200)
        except Course.DoesNotExist:
            return render(request, 'Dynamic_Message.html', context={'message': 'درس مورد نظر یافت نشد'}, status=404)
        except Exception as e:
            print(e)
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجدد تلاش بفرمایید'},status=500)






class Update_Exam(View):
    def get(self,request,course_id):
        try:
            exam=Exam.objects.get(course_id=course_id,course__teacher=request.user)
            frm=Exam_Form(instance=exam)
            return render(request,'Update_&_Create_Exam.html',context={'form':frm,'to_do':'update','course_name':exam.course.title,'course_id':exam.course_id},status=200)
        except Exam.DoesNotExist:
            return render(request,'Dynamic_Message.html',context={'message':'امتحانی با مشخصات وارد شده یافت نشد'},status=404)
        except:
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجدد تلاش بفرمایید'},status=500)
    def post(self,request,course_id):
        try:
            exam=Exam.objects.get(course_id=course_id,course__teacher=request.user)
            frm=Exam_Form(data=request.POST,instance=exam)
            print(request.POST)
            if frm.is_valid():
               frm.save()
               return redirect(reverse('teacher_courses'))
            else:
                return render(request,'Update_&_Create_Exam.html',context={'form':frm,'to_do':'update','course_name':exam.course.title,'course_id':exam.course_id},status=400)
        except Exam.DoesNotExist:
            return render(request,'Dynamic_Message.html',context={'message':'امتحانی با مشخصات وارد شده یافت نشد'},status=404)
        except Exception as e:
            print(e)
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجددا تلاش بفرمایید'},status=500)

class Student_Exams(ListView):
    template_name = 'Student_Exams.html'
    model=Course
    context_object_name = 'courses'
    paginate_by = 20
    def get_queryset(self):
        has_exam=Exam.objects.filter(course_id=OuterRef('pk'))
        sem_id=self.request.session.get('session') or Current_Semester.objects.first().semester.id
        has_answer=Exam_Answer.objects.select_related('exam').filter(author_id=self.request.user.id,exam__course_id=OuterRef('pk'))
        query=self.request.user.attending_courses.all().annotate(has_exam=Exists(has_exam)).filter(has_exam=True,semester_id=sem_id).select_related('exam').annotate(
            exam_date=F('exam__start_time'),duration=(F('exam__end_time')-F('exam__start_time')),has_answer=Exists(has_answer)
        ).annotate(t=F('exam_date__day')).order_by('-exam_date')
        return query


class Submit_Exam_Answer(View):
    def get(self,request,course_id):
        try:
            current_date=datetime.datetime.now(datetime.timezone.utc)

            exam=Exam.objects.get(course_id=course_id,course__students=request.user)
            print('current',current_date, exam.start_time,exam.end_time,current_date>exam.start_time,current_date<exam.end_time)
            if current_date<exam.start_time:
                return render(request,'Dynamic_Message.html',context={'message':'امتحان هنوز شروع نشده است!'},status=401)
            elif current_date>exam.end_time:
                return render(request, 'Dynamic_Message.html', context={'message': 'فرصت ثبت پاسخ برای این درس به پایان رسیده است'},
                              status=401)
            else:
                answer, a = Exam_Answer.objects.get_or_create(exam_id=exam.id, author_id=request.user.id)
                frm = Exam_Answer_Form(instance=answer)
                return render(request, 'Submit_Exam_Answer.html',
                              context={'form': frm, 'course_name': exam.course.title,'course_id':course_id}, status=200)

        except Exam.DoesNotExist:
            return render(request,'Dynamic_Message.html',context={'message':'آزمونی با مشخصات وارد شده پیدا نشد!'},status=404)
        except Exception as e:
            print(e)
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجددا تلاش بفرمایید'},status=500)
    def post(self,request,course_id):
        try:
            current_date=datetime.datetime.now(datetime.timezone.utc)
            exam=Exam.objects.get(course_id=course_id,course__students=request.user)
            if current_date < exam.start_time:
                return render(request, 'Dynamic_Message.html', context={'message': 'امتحان هنوز شروع نشده است!'},
                              status=401)
            elif current_date > exam.end_time:
                return render(request, 'Dynamic_Message.html',
                              context={'message': 'فرصت ثبت پاسخ برای این درس به پایان رسیده است'},
                              status=401)
            else:
                answer, a = Exam_Answer.objects.get_or_create(exam_id=exam.id, author_id=request.user.id)
                frm = Exam_Answer_Form(instance=answer, data=request.POST, files=request.FILES)
                if frm.is_valid():
                    frm.save()
                    return render(request, 'Dynamic_Message.html',
                                  context={'message': 'پاسخ شما با موفقیت ثبت شد'}, status=200)
                else:
                    return render(request, 'Submit_Exam_Answer.html',
                                  context={'form': frm, 'course_name': exam.course.title,'course_id':course_id}, status=401)


        except Exam.DoesNotExist:
            return render(request,'Dynamic_Message.html',context={'message':'آزمونی با مشخصات وارد شده پیدا نشد!'},status=404)
        except Exception as e:
            print(e)
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجددا تلاش بفرمایید'},status=500)


class Students_Answers(ListView):
    template_name = 'Students_Answers.html'
    context_object_name = 'students'
    model=User
    def get_queryset(self):
        course=get_object_or_404(Course,id=self.kwargs['course_id'],teacher=self.request.user)
        answer=Exam_Answer.objects.select_related('exam').filter(exam__course_id=course.id)
        query=course.students.all().prefetch_related('exams_answers',Prefetch('exams_answers',queryset=answer,to_attr='answer'))
        print(query)
        return query