from django import forms
from .models import Course,Score_Appeal
class Course_Filter_Form(forms.Form):
    department=forms.CharField(widget=forms.Select(choices=Course.department_choices),label='دانشکده')
    title=forms.CharField(label='عنوان درس')
    for_degrees=forms.CharField(widget=forms.Select(choices=Course.degree_choices),label='مقطع')
    course_type=forms.CharField(widget=forms.Select(choices=Course.course_types),label='نوع درس')


class Appeal_Form(forms.ModelForm):
    class Meta:
        model=Score_Appeal
        fields=['text']
        labels={'text':'متن اعتراض'}
        widgets={'text':forms.Textarea()}