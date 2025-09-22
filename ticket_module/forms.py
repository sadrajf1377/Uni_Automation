from django import forms

from .models import Ticket,User_Message

class Ticket_Form(forms.ModelForm):
    class Meta:
        model=Ticket
        fields=['title','subject']


class Message_Form(forms.ModelForm):
    class Meta:
        model=User_Message
        fields=['ticket','text','thumb']
        widgets={'text':forms.Textarea(),'thumb':forms.FileInput(),'ticket':forms.HiddenInput()}
