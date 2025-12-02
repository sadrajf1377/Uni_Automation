from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Window, F, Case, When, Value, CharField, OuterRef, Subquery
from django.db.models.functions import RowNumber, Lag
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from .forms import News_Form
from .models import News,News_Images
from semester_module.models import Semester,Current_Semester
# Create your views here.

@method_decorator(login_required,name='dispatch')
class Index_Page(ListView):
    template_name = 'Index_Page.html'
    context_object_name = 'news'
    model=News
    ordering = '-date'
    paginate_by = 20
    def get_queryset(self):
        thumb=News_Images.objects.filter(news_id=OuterRef('pk')).order_by('-id').values_list('image',flat=True)[:1:]
        query=super().get_queryset().annotate(thumbnail=Subquery(thumb)).select_related('author')
        for o in query:
            print(o.title,o.thumbnail)
        return query
class Create_News(View):
    def get(self,request):
        frm=News_Form()
        return render(request,'Create_News.html',context={'form':frm},status=200)
    def post(self,request:HttpRequest):
        frm = News_Form(request.POST, request.FILES)
        try:
            files=request.FILES.getlist('news_imgs')
            if next((file for file in files if file.size > 1500000),None):
                frm.add_error('title','اندازه فایل تصویر باید کمتر از 1.5 مگابایت باشد')
                return render(request, 'Create_News.html', context={'form': frm}, status=400)
            imgs=[]
            if frm.is_valid():
                with transaction.atomic():
                    news=frm.save()
                    for file in files:
                        imgs.append(News_Images(image=file,news_id=news.id))
                    News_Images.objects.bulk_create(imgs)

                return render(request, 'Dynamic_Message.html', context={'message': 'خبر جدید با موفقیت درج شد!'},
                              status=201)
            else:
                return render(request, 'Create_News.html', context={'form': frm}, status=400)
        except Exception as e:
            print(e)
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجددا تلاش بفرمایید!'},status=500)


