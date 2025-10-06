import datetime

from django import forms

from .models import Exam,Exam_Answer

class Exam_Form(forms.ModelForm):
    class Meta:
        model=Exam
        fields=['start_time','end_time']
        widgets={'start_time':forms.DateTimeInput(),'end_time':forms.DateTimeInput()}
    def clean(self,*args):
        current_date=datetime.datetime.now()
        start_date=datetime.datetime.strptime(self.data.get('start_time'),"%Y-%m-%d %H:%M:%S")
        end_date=datetime.datetime.strptime(self.data.get('end_time'),"%Y-%m-%d %H:%M:%S")
        if start_date.date() < current_date.date():
            self.add_error('start_time','تاریخ امتحان نمی تواند قبل از تاریخ فعلی سیستم باشد')
        if start_date>end_date:
            self.add_error('end_time','زمان شروع امتحان نمی تواند پس از آغاز آن باشد')
        super().clean(*args)


class Exam_Answer_Form(forms.ModelForm):
    class Meta:
        model=Exam_Answer
        fields=['file','description']
        widgets={'file':forms.FileInput(),'description':forms.Textarea()}