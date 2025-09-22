from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView
from .models import Semester, Current_Semester
from .forms import Semester_Form,Change_Semester_Form,Change_Semester_Global_Form
from django.core.cache import caches
# Create your views here.
class Create_Semester(CreateView):
    template_name = 'General_Form.html'
    context_object_name = 'form'
    model=Semester
    success_url = reverse_lazy('index')
    form_class = Semester_Form
    def get_context_data(self, **kwargs):
        context=super().get_context_data()
        context['url_name']='create_semester'
        context['title']='تعریف نیمسال جدید'
        return context


class Change_Semester(View):
    def post(self,request):
        frm=Change_Semester_Form(request.POST)
        if frm.is_valid():
            try:
                semester_id = frm.cleaned_data.get('semester_id')
                sem = Semester.objects.get(id=semester_id)
                request.session.update({'semester': sem.id})
                return redirect(reverse('index'))
            except Semester.DoesNotExist:
                frm.add_error('semester_id','نیمسال یافت نشد')
                return render(request,'General_Form.html',context={'form':frm,'url_name':'change_semester'},status=404)
            except Exception:
                frm.add_error('semester_id','مشکلی در تغییر نیمسال به وجود آمد!لطفا مجدد تلاش بفرمایید')
                return render(request, 'General_Form.html', context={'form': frm, 'url_name': 'change_semester'},status=500)


    def get(self,request):
        frm=Change_Semester_Form()
        return render(request,'General_Form.html',context={'form':frm,'url_name':'change_semester'},status=200)


class Change_Global_Semester(View):
    def get(self,request):
        frm = Change_Semester_Global_Form(instance=Current_Semester.objects.first())
        return render(request, 'General_Form.html', context={'form': frm, 'url_name': 'change_global_semester'}, status=200)
    def post(self,request):
        frm = Change_Semester_Global_Form(data=request.POST,instance=Current_Semester.objects.first())
        if frm.is_valid():
            try:
                ins=frm.instance
                id=ins.semester.id
                print(id)
                ch=caches['default']
                ch.set('global_semester',id)
                frm.save()
                return render(request,'Dynamic_Message.html',context={'message':f' نیسمال فعلی برای تمام کاربران سیستم به'
                                                                                f'{ins.semester.start_date} تغییر کرد'})

            except Exception as e:
                frm.add_error('semester',str(e.args))
                return render(request,'General_Form.html',context={'form':frm,'url_name':'change_global_semester'},status=500)
        else:
            return render(request, 'General_Form.html', context={'form': frm, 'url_name': 'change_global_semester'},
                          status=401)

