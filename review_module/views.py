import json

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import OuterRef, Exists
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from course_module.models import Course
from semester_module.models import Semester,Current_Semester
from .models import Review_Session, Reviews

from user_module.models import User
# Create your views here.
class Teachers_To_Review(ListView):
    template_name = 'Teachers_To_Review.html'
    model=Course
    context_object_name = 'courses'
    ordering = '-exam_time'
    def get_queryset(self):
        sem=self.request.session.get('semester') or Current_Semester.objects.first().semester.id
        q=Review_Session.objects.filter(semester_id=sem,teacher=OuterRef('teacher_id'),student_id=self.request.user.id,session_closed=True)
        query=super().get_queryset().filter(semester_id=sem,students=self.request.user).select_related('teacher').annotate(is_closed=Exists(q))
        return query


class Load_Review(View):
    def get(self,request,teacher_id):
        try:
            sem = request.session.get('semester') or Current_Semester.objects.first().semester.id
            session,s=Review_Session.objects.get_or_create(student_id=request.user.id,teacher_id=teacher_id,session_closed=False,semester_id=sem)
            reviews=session.reviews.all()
            return render(request,'Review_Teachers.html',context={'reviews':reviews,'review_session_id':session.id})
        except IntegrityError as e:
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد'+str(e)},status=409)
        except ValidationError as e:
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد'+str(e)},status=409)
        except Exception as e:
            return render(request, 'Dynamic_Message.html',
                          context={'message': ' مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجددا تلاش بفرمایید یا با پشتیبانی تماس بگیرید!'}, status=500)




class Update_Review_Session(View):
    def post(self,request):
        try:
            with transaction.atomic():
                sem = request.session.get('semester') or Current_Semester.objects.first().semester.id
                data = json.loads(request.body)

                session = Review_Session.objects.get(id=data['review_session_id'], student=request.user,
                                                     semester_id=sem)
                reviews = list(session.reviews.all())
                reviews_answers = data['reviews_answers']
                for rev in reviews:
                    rev.review = reviews_answers.get(str(rev.id))
                print(reviews_answers)
                Reviews.objects.bulk_update(reviews, fields=['review'])
                return JsonResponse(data={'message': 'تغییرات با موفقیت اعمال شد'}, status=201)



        except KeyError:
             return JsonResponse(data={'message':'مقادیر وارد شده صحیح نمی باشند'},status=402)
        except Review_Session.DoesNotExist:
            return JsonResponse(data={'message':'استاد مربوطه برای ارشیابی یافت نشده'},status=404)
        except ValidationError as e:
            return JsonResponse(
                data={'messsage': 'مشکلی در پردازش درخواست شما به وجود آمد!لطفا بخش خطاها را بررسی بفرمایید!', 'error': str(e)},
                status=409)
        except IntegrityError as e:
            return JsonResponse(
                data={'messsage': 'مشکلی در پردازش درخواست شما به وجود آمد!لطفا بخش خطاها را بررسی بفرمایید!', 'error': str(e)},
                status=409)

        except Exception as e:
            return JsonResponse(data={'messsage':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجدد تلاش بفرمایید!'},status=500)




class Close_Review_Session(View):
    def post(self,request):
        try:
            sem = request.session.get('semester') or Current_Semester.objects.first().semester.id
            session = get_object_or_404(Review_Session, student_id=request.user.id, id=request.POST.get('session_id'),
                                        semester_id=sem,session_closed=False)
            session.session_closed = True
            session.save()
            return redirect(reverse('teachers_to_review'))
        except KeyError:
            return render(request, 'Dynamic_Message.html',
                          context={'message': 'داده وارد شده صحیح نمی باشد!لطفا مجدد تلاش بفرمایید'},
                          status=401)
        except Exception as e:
            print(e)
            return render(request,'Dynamic_Message.html',context={'message':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجدد تلاش بفرمایید!'},status=500)



