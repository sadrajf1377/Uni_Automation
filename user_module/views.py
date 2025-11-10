from django.db.models import Q, Count, F, OuterRef, Subquery, Window, Case, When, Value, CharField, ExpressionWrapper, \
    Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import UpdateView, ListView
from .models import Student_Profile, Employee_Profile, Teacher_Profile, User,General_Profile
from .forms import Student_Profile_Form,Employee_Profile_Form,Teacher_Profile_Form,Student_Search_Form,Teacher_Search_Form,Employee_Search_Form
from utils.decorators import restrict_view_access
profiles_dict={'دانشجو':[Student_Profile_Form,Student_Profile],'استاد':[Teacher_Profile_Form,Teacher_Profile],'کارمند یا کارشناس':[Employee_Profile_Form,Employee_Profile]}

class Update_Profile(View):
    def get(self,request):
        type=request.user.user_type
        instance,i=profiles_dict[type][1].objects.get_or_create(user=request.user)
        frm=profiles_dict[type][0](instance=instance)
        return render(request,'Update_Profile.html',context={'frm':frm})
    def post(self,request):
        type = request.user.user_type
        instance, i = profiles_dict[type][1].objects.get_or_create(user=request.user)
        frm = profiles_dict[type][0](instance=instance,data=request.POST,files=request.FILES)
        if frm.is_valid():
            frm.save()
            return redirect(reverse('index'))
        else:
            return render(request, 'Update_Profile.html', context={'frm': frm})

@method_decorator(restrict_view_access(['teacher'],['رییس دانشکده']),name='dispatch')
class Search_Users(ListView):
    template_name = 'USers_List.html'
    model = User
    context_object_name = 'users'
    paginate_by = 20
    ordering = '-date_joined'
    def get_queryset(self):
        number=self.kwargs['national_number'] or '__all__'
        last_name=self.kwargs['last_name'] or '__all__'
        condition=Q()
        if number!='__all__':
            condition&=Q(national_number__iecontains=number)
        if last_name!='__all__':
            condition&=Q(last_name__iecontains=last_name)
        query=super().get_queryset().filter(condition).values('national_number','first_name','last_name','avatar')
        return query


@method_decorator(restrict_view_access(['teacher'],['رییس دانشکده']),name='dispatch')
class Change_User_Profile_Status(View):
    def post(self,request):
        try:
            type=request.POST.get('user_type')
            user_id=request.POST.get('user_id')
            profile=profiles_dict[type][1].objects.get(user_id=user_id)
            profile.is_approved=request.POST.get('status')=='approved'
            profile.save()
            return  render(request,'Dynamic_Message.html',context={
            'message':f'وضعیت کاربر {profile.user.first_name} به {"تایید شده" if profile.is_approved else "تایید نشده"} تغییر کرد'},status=201)

        except General_Profile.DoesNotExist:
            return render(request,'Dynamic_Message.html',context={'message':'پروفایل کاربری با مشخصات وارد شده یافت نشد'},status=404)
        except Exception as e:
            return render(request, 'Dynamic_Message.html',
                          context={'message': 'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجددا تلاش بفرمایید'}, status=500)

class Update_User_Info(UpdateView):
    model = User
    fields=['phone_number','first_name','national_number','last_name']
    template_name = 'Update_User_Info.html'
    success_url = reverse_lazy('index')
    context_object_name = 'info_form'
    def get_object(self, queryset=None):
        obj=self.request.user
        return obj


class Teachers_Sorted_By_Ratings(ListView):
    template_name = 'Teachers_Ratings.html'
    model = User
    context_object_name = 'teachers'
    paginate_by = 20
    def get_queryset(self):
        query=User.objects.filter(user_type='استاد').prefetch_related('teacher_review__reviews').annotate(total=Count('teacher_review'),great=Count('teacher_review__reviews',filter=Q(teacher_review__reviews__review='عالی')),
                                                                                good=Count('teacher_review__reviews',filter=Q(teacher_review__reviews__review='خوب')),neg=Count('teacher_review__reviews',filter=Q(teacher_review__reviews__review='ضعیف')),
                                    awful=Count('teacher_review__reviews',filter=Q(teacher_review__reviews__review='خیلی ضعیف')),rank=F('teacher_profile__rank')).annotate(overall=F('great')*4+F('good')*2+F('neg')*-2+F('awful')*-4).exclude(total=0).values('overall','username','rank').order_by('-overall')
        return query

# Create your views here.
@method_decorator(restrict_view_access(['teacher'],['رییس دانشکده']),name='dispatch')
class Load_Profiles_Filters(View):
    def get(self,request):
        student_frm=Student_Search_Form()
        teacher_frm=Teacher_Search_Form()
        employee_form=Employee_Search_Form()
        return render(request,'Filter_Profiles.html',context={'teacher_frm':teacher_frm,'student_frm':student_frm,'employee_frm':employee_form},status=200)

@method_decorator(restrict_view_access(['teacher'],['رییس دانشکده']),name='dispatch')
class UnApproved_Users(ListView):
    template_name = 'Unapproved_Profiles.html'
    model = User
    context_object_name = 'users'
    paginate_by = 20
    ordering = '-date_joined'

@method_decorator(restrict_view_access(['teacher'],['رییس دانشکده']),name='dispatch')
class UnApproved_Students(UnApproved_Users):
    def get_queryset(self):
        #'department','degree','current_degree_code'
        department=self.kwargs['department']
        degree=self.kwargs['degree']
        query=super().get_queryset().filter(user_type='دانشجو').select_related('student_profile').filter(student_profile__is_approved=False,student_profile__department=department
                                                                              ,student_profile__degree=degree).annotate(profile_id=F('student_profile__id'))
        return query

@method_decorator(restrict_view_access(['teacher'],['رییس دانشکده']),name='dispatch')
class UnApproved_Teachers(UnApproved_Users):
    def get_queryset(self):
        #'department','rank','latest_degree_code'
        department=self.kwargs['department']
        rank=self.kwargs['rank']

        query=super().get_queryset().filter(user_type='استاد').select_related('teacher_profile').filter(teacher_profile__is_approved=False,teacher_profile__department=department
                                                                                                          ,teacher_profile__rank=rank).annotate(profile_id=F('teacher_profile__id'))
        return query

@method_decorator(restrict_view_access(['teacher'],['رییس دانشکده']),name='dispatch')
class UnApproved_Employees(UnApproved_Users):
    def get_queryset(self):
        #'role', 'latest_degree_code'
        role=self.kwargs['role']
        query=super().get_queryset().filter(user_type='کارمند یا کارشناس').select_related('employee_profile').filter(employee_profile__is_approved=False,
                                                                                    employee_profile__role=role).annotate(profile_id=F('employee_profile__id'))
        return query

@method_decorator(restrict_view_access(['teacher'],['رییس دانشکده']),name='dispatch')
class Approve_User(View):
    def post(self,request,profile_id,profile_type):
        try:
            profs_dict = {'student': Student_Profile, 'teacher': Teacher_Profile, 'employee': Employee_Profile}
            prof = profs_dict[profile_type].objects.get(id=profile_id)
            prof.is_approved = True
            prof.save()
            return render(request, 'Dynamic_Message.html', context={'message': 'حساب کاربری با موفقیت تایید شد!'},
                          status=201)
        except General_Profile.DoesNotExist as e:
            return render(request,'Dynamic_Message.html',context={'message':'حسابی با این مشخصات پیدا نشد'},status=404)
        except KeyError:
            return render(request, 'Dynamic_Message.html', context={'message': 'نوع حساب وارد شده نامعتبر می باشد'},
                          status=404)
        except Exception as e:
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد'},status=500)

    def get(self,request,profile_id,prof_type):
        try:
            profs_dict = {'student': Student_Profile, 'teacher': Teacher_Profile, 'employee': Employee_Profile}
            prof = profs_dict[prof_type].objects.get(id=profile_id)
            return render(request, 'View_Unapproved_Profile.html', context={'profile': prof,'prof_type':prof_type},
                          status=200)
        except General_Profile.DoesNotExist as e:
            return render(request, 'Dynamic_Message.html', context={'message': 'حسابی با این مشخصات پیدا نشد'},
                          status=404)
        except KeyError:
            return render(request, 'Dynamic_Message.html', context={'message': 'نوع حساب وارد شده نامعتبر می باشد'},
                          status=404)
        except Exception as e:
            return render(request, 'Dynamic_Message.html',
                          context={'message': 'مشکلی در پردازش درخواست شما به وجود آمد'}, status=500)

class Departments_List(View):
    def get(self,request):
        cases=Case(When(user_type='دانشجو',then=F('student_profile__department')),
                   When(user_type='استاد',then=F('teacher_profile__department')),
                   When(user_type='کارمند یا کارشناس',then=F('employee_profile__department')),output_field=CharField())
        s=User.objects.all().annotate(dep=cases).values('dep').annotate(students=Count('student_profile',distinct=True)
                                                                        ,teachers=Count('teacher_profile',distinct=True),employees=Count('employee_profile',distinct=True),courses=Count('teacher_courses'),
                                                                        avg=Sum(F('scores__score')*F('scores__course__credits'))/Sum('scores__course__credits'))
        print(s)
        return render(request,'Departments.html',context={'departments':s},status=201)