from django.forms import ModelForm
from django import forms
from .models import Semester,Current_Semester
class Semester_Form(ModelForm):
    class Meta:
        model=Semester
        fields='__all__'
        widgets={'start_date':forms.SelectDateWidget(),'end_date':forms.SelectDateWidget()}

class Change_Semester_Form(forms.Form):
    semester_id = forms.CharField(widget=forms.Select(choices=(1,2)),
                                  label='نیمسال')

class Change_Semester_Global_Form(forms.ModelForm):
    class Meta:
        model=Current_Semester
        fields='__all__'
