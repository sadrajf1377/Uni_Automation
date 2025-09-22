from django.contrib import admin
from .models import Ticket,User_Message,Support_Response
class Ticket_Display(admin.ModelAdmin):
    list_display = ['title','date','creator']
    list_display_links = ['title']
admin.site.register(User_Message)
admin.site.register(Ticket,Ticket_Display)
admin.site.register(Support_Response)
# Register your models here.
