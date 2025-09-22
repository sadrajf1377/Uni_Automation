from django import forms

from .models import Employee_Profile,Student_Profile,Teacher_Profile

general_profile_fields=['avatar','area_code','sex','latest_degree','latest_certificate_picture','latest_degree_code','department']


class Teacher_Profile_Form(forms.ModelForm):
    class Meta:
        model=Teacher_Profile
        fields=['rank','role','is_faculty']+general_profile_fields
        widgets={'department':forms.Select(),'avatar':forms.FileInput(),'latest_certificate_picture':forms.FileInput()}
        labels={}

class Employee_Profile_Form(forms.ModelForm):
    class Meta:
        model=Employee_Profile
        fields=['role']+general_profile_fields
        widgets = {'department': forms.Select(), 'avatar': forms.FileInput(),
                   'latest_certificate_picture': forms.FileInput()}

class Student_Profile_Form(forms.ModelForm):
    class Meta:
        model=Student_Profile
        fields=general_profile_fields+['degree']
        widgets = {'department': forms.Select(), 'avatar': forms.FileInput(),
                   'latest_certificate_picture': forms.FileInput()}


class Student_Search_Form(forms.ModelForm):
    class Meta:
        model=Student_Profile
        fields=['department','degree']

class Teacher_Search_Form(forms.ModelForm):
    class Meta:
        model=Teacher_Profile
        fields=['department','rank']

class Employee_Search_Form(forms.ModelForm):
    class Meta:
        model=Employee_Profile
        fields=['role']