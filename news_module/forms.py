from .models import News
from django import forms

class News_Form(forms.ModelForm):
    class Meta:
        model=News
        fields=['title','content']
        widgets={'title':forms.TextInput(),'content':forms.Textarea()}

