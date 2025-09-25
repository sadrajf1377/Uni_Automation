import re

from django import forms
from user_module.models import User


pass_pattern=r'(?=.*[0-9].*)(.*[A-Z].*)(.*[a-z].*)'
class Login_Form(forms.Form):
    national_number=forms.CharField(max_length=10,required=True,label='شماره ملی',widget=forms.TextInput())
    password=forms.CharField(max_length=200,required=True,label='رمز عبور',widget=forms.PasswordInput())
    def clean(self):

        nat_number:str=self.data.get('national_number')
        if (not nat_number.isnumeric()) or len(nat_number)!=10:
            self.add_error('national_number','شماره ملی فقط شامل کاراکتر عددی می باشد و بایستی ده کاراکتر داشته باشد')
        super().clean()

class Temp_Code_Login_Form(forms.Form):
    nat_number=forms.CharField(max_length=10,required=True,widget=forms.HiddenInput())
    temp_code=forms.CharField(max_length=16,required=True,label='کد موقت ارسال شده به ایمیل شما')
    def clean(self):
        print(self.data)
        nat_number:str=self.data.get('nat_number')

        if (not nat_number.isnumeric()) or len(nat_number)!=10:
            self.add_error('national_number','شماره ملی فقط شامل کاراکتر عددی می باشد و بایستی ده کاراکتر داشته باشد')
        super().clean()



class Signup_Form(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','national_number','email','phone_number','user_type','password']
        widgets={'email':forms.EmailInput(),'password':forms.PasswordInput(),'user_type':forms.Select()}
        labels={'first_name':'نام','last_name':'نام خانوادگی','email':'ایمیل'}
    password_repeat=forms.CharField(widget=forms.PasswordInput(),label='تکرار رمز عبور',required=True)
    def clean(self):

        password=self.data.get('password')
        password_repeat=self.data.get('password_repeat')
        if not password == password_repeat:
            self.add_error('password_repeat','رمز عبور و تکرار آن یکی نیستند!')
        if not re.match(pass_pattern,password) or len(password)<8:
            self.add_error('password',' رمز عبور باید شامل حداقل یک حرف بزرگ،یک حرف کوچک،یک عدد و  8 کاراکتر باشد')
        super().clean()
