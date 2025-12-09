from django import forms

from .models import Ticket,User_Message,Support_Response

class Ticket_Form(forms.ModelForm):
    class Meta:
        model=Ticket
        fields=['title','subject']


class Message_Form(forms.ModelForm):
    class Meta:
        model=User_Message
        fields=['ticket','text','thumb']
        widgets={'text':forms.Textarea(),'thumb':forms.FileInput(),'ticket':forms.HiddenInput()}

class Response_Form(forms.ModelForm):
    class Meta:
        model=Support_Response
        fields=['parent_message','text','thumb']
        widgets={'parent_message':forms.HiddenInput(),'text':forms.Textarea(),'thumb':forms.FileInput()}
        labels={'text':'متن پاسخ','thumb':'تصویر پاسخ (اختیاری)'}