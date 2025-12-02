from django.db import transaction
from django.db.models import Count, Q, When, Case, Value, IntegerField, Prefetch, OuterRef
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView
from .models import Ticket,User_Message,Support_Response
from .forms import Ticket_Form,Message_Form
from user_module.models import User
# Create your views here.
class My_Tickets_List(ListView):
    template_name = 'User_Tickets.html'
    context_object_name = 'tickets'
    model=Ticket
    paginate_by = 20
    def get_queryset(self):
        user=self.request.user
        query=user.tickets.prefetch_related('messages').annotate(unread_response=Count('messages__responses',filter=Q(
            messages__responses__is_read=False
        ),status=Case(When(is_closed=True,then=Value(value=1)),default=-1,output_field=IntegerField()))).order_by('-unread_response','-date')
        return query
    def get_context_data(self, *, object_list=None, **kwargs):
        context=super().get_context_data()
        context['ticket_form']=Ticket_Form()
        return context

class Create_New_Ticket(View):
    def post(self,request:HttpRequest):
        frm=Ticket_Form(request.POST)
        if frm.is_valid():
            try:
                with transaction.atomic():
                    frm.instance.creator=request.user
                    frm.save()
                    return JsonResponse(data={'message':'تیکت با موفقیت ساخته شد!'},status=201)
            except:
                return JsonResponse(data={'message':'مشکلی در ساخت تیکت به وجود آمد!لطفا مجددا تلاش بفرمایید'},status=500)
        else:
            fields=frm.errors
            errors=''
            for field in fields:
                for error in frm.errors[field]:
                    errors+=error+'\n'
            return JsonResponse(data={'message':'داده ورودی صحیح نمی باشد!','errors':errors},status=401)

class Ticket_Messages(ListView):
    template_name = 'Ticket_Messages.html'
    model=User_Message
    context_object_name = 'messages'
    paginate_by = 20
    def get_queryset(self):
        ticket=get_object_or_404(Ticket,creator=self.request.user,id=self.kwargs['ticket_id'])
        messages=ticket.messages.prefetch_related(Prefetch('responses',Support_Response.objects.all().order_by('-date'),to_attr='sup_responses')).annotate(unread_count=Count('responses',filter=Q(responses__is_read=False))).order_by('unread_count','date')
        return messages
    def get_context_data(self, *, object_list=None, **kwargs):
        context=super().get_context_data()
        context['message_form']=Message_Form(initial={'ticket':self.kwargs['ticket_id']})
        return context


class Write_Message(View):
    def post(self,request):
        frm=Message_Form(request.POST,request.FILES)
        if frm.is_valid():
            try:
                with transaction.atomic():
                    ticket_id=frm.cleaned_data.get('ticket').id
                    request.user.tickets.get(id=ticket_id)
                    mes=frm.save()
                    return JsonResponse(data={'message':'پیام با موفقیت ثبت شد!','message_content':mes.text,'date':mes.date},status=201)
            except Ticket.DoesNotExist:
                return JsonResponse(data={'message': 'تیکت وارد شده معتبر نمی باشد'}, status=404)
            except Exception as e:
                print('exception is ',e)
                return JsonResponse(data={'message':'مشکلی در ثبت پیام شما به وجود آمد!لطفا مجددا تلاش بفرمایید'},status=500)
        else:
            errors=''
            fields=frm.errors
            print(frm.errors)
            for field in fields:
                for error in frm.errors[field]:
                    errors+=error
            return JsonResponse(data={'message':'داده ورودی نامعتبر می باشد!','errors':errors},status=401)


class Mark_Response_As_Read(View):
    def post(self,request):
        try:
            response_id=request.POST.get('response_id')
            response = Support_Response.objects.select_related('parent_message__ticket').get(
                parent_message__ticket__creator=request.user, id=response_id)
            response.is_read = True
            response.save()
            return JsonResponse(data={'message': 'وضعیت پاسخ به خوانده شده تغییر کرد'}, status=201)
        except Support_Response.DoesNotExist:
            return JsonResponse(data={'message':'پاسخی با این مشخصات یافت نشد!'},status=404)
        except KeyError:
            return JsonResponse(data={'message':'اطلاعات مورد نیاز یافت نشد'},status=401)
        except:
            return JsonResponse(data={'message':'مشکلی در پردازش درخواست شما به وجود آمد!'},status=500)


