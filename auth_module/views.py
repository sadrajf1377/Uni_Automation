import datetime

import redis
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from django.core.cache import caches
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views import View
from .forms import Login_Form,Temp_Code_Login_Form,Signup_Form
from user_module.models import User
from utils.email_service import send_emails
# Create your views here.
class Login(View):
    def get(self,request):
        return render(request,'Login.html',context={'login_form':Login_Form()})
    def post(self,request):
        frm=Login_Form(request.POST)
        if frm.is_valid():
            nat_number=frm.cleaned_data.get('national_number')
            password=frm.cleaned_data.get('password')
            try:
                user=User.objects.get(national_number=nat_number)
                if user.check_password(password):
                    code=get_random_string(length=15)
                    red=redis.StrictRedis('redis://redis:6379/1')
                    red.hset('temp_codes',nat_number,code,exp=60*2)
                    send_emails.delay(template_name='Temp_Code_Email.html',context={'code':code},to=user.email,subject='رمز ورود یکبار مصفرف')
                    return render(request,'Temp_Code_Login.html',context={'tmp_form':Temp_Code_Login_Form(initial={'nat_number':nat_number})},status=200)
                else:
                    frm.add_error('password','کاربری با این مشخصات یافت نشد!')
                    return render(request, 'Login.html', context={'login_form':frm},status=404)
            except User.DoesNotExist:
                frm.add_error('password', 'کاربری با این مشخصات یافت نشد!')
                return render(request, 'Login.html', context={'login_form': frm},status=404)
            except Exception as e:
                frm.add_error('password','مشکلی در هنگا پردازش درخواست شما به وجود آمد!لطفا مجدد تلاش بفرمایید')
                return render(request, 'Login.html', context={'login_form': frm}, status=500)
        else:
            return render(request, 'Login.html', context={'login_form': frm},status=401)


class Generate_New_Temp_Code(View):
    def post(self,request):
            nat_number=request.POST.get('nat_number')
            red=redis.StrictRedis('redis://redis:6379/1')
            dic = red.hget('temp_codes')[nat_number] or None
            if dic:
                return JsonResponse(data={'message':'رمز موقت قبلی هنوز برای شما معتبر است،تا زمان منقضی شدن رمز قبلی،امکان تولید رمز جدید وجود ندارد.عمر هر رمز:2 دقیقه'})
            else:
                try:
                     user=User.objects.get(national_number=nat_number)
                     code = get_random_string(length=15)
                     send_emails.delay(template_name='Temp_Code_Email.html',subject='رمز عبور موقت',context={'code':code},to=user.email)
                     red.hset('temp_codes', nat_number,code,exp=60*2)
                     return JsonResponse(data={'message':'رمز موقت جدید برای شما به ایمیلتان ارسال شد'},status=201)
                except User.DoesNotExist:
                    return JsonResponse(data={'message':'کاربری با این شماره ملی وجود ندارد!'},status=404)
                except Exception as e:
                    return JsonResponse(data={'message':'مشکلی در پردازش درخواست شما به وجود آمد!لطفا مجدد تلاش بفرمایید!'},status=500)




class Login_With_Temp_Code(View):
    def post(self,request):
        frm=Temp_Code_Login_Form(request.POST)
        if frm.is_valid():
            temp_code = frm.cleaned_data.get('temp_code')
            nat_number = frm.cleaned_data.get('nat_number')
            red=redis.StrictRedis('redis://redis:6379/1')
            code = red.hget('temp_codes')[nat_number]['code'] or None
            if code and temp_code == code:
                login(user=request.user, request=request)
                return redirect(reverse('index'))
            else:
                frm.add_error('temp_code', 'کد وارد شده معتبر نمی باشد!')
                return render(request, 'Temp_Code_Login.html',
                                  context={'tmp_form':frm},
                                  status=401)
        else:
            return render(request, 'Temp_Code_Login.html',
                          context={'tmp_form': frm},
                          status=401)

class Signup(View):
    def get(self,request):
        return render(request,'Signup.html',context={'signup_form':Signup_Form()},status=200)
    def post(self,request):
        frm=Signup_Form(request.POST)
        if frm.is_valid():
            red=redis.StrictRedis('redis://redis:6379/1')
            code=get_random_string(length=64)
            data=frm.cleaned_data
            data['password']=make_password(data.get('password'))
            del data['password_repeat']
            red.hset('temp_users',code,data,exp=60*15)
            send_emails.delay(subject='فعالسازی حساب',template_name='Account_Activation_Email.html',context={'act_code':code},to=data.get('email'))
            return render(request,'Dynamic_Message.html',context={'message':'برای فعالسازی حساب خود،به ایمیلی که وارد کردید مراجعه فرمایید!'},status=201)
        else:
            return render(request,'Signup.html',context={'signup_form':frm},status=401)


class Activate_Account(View):
    def get(self,request,act_code):
        try:
            red=redis.StrictRedis('redis://redis:6379/1')
            data = redis.hget('temp_users')[act_code]
            frm = Signup_Form(data=data)
            if frm.is_valid():
                frm.save()
                red.hdel(act_code)
                return render(request, 'Dynamic_Message.html', context={'message': 'حساب شما با موفقیت فعال شد'},
                              status=201)
            else:
                return render(request,'Dynamic_Message.html',context={'message':str(frm.errors)},status=401)

        except KeyError:
            return render(request,'Dynamic_Message.html',context={'message':'کاربری با این شماره فعالسازی پیدا نشد!'},status=404)


def logout_user(request):
    if request.method=='POST':
        logout(request=request)
        return redirect(reverse('index'))