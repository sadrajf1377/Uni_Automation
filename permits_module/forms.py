from django import forms

from .models import Permit
class Permit_Form(forms.ModelForm):
    class Meta:
        model=Permit
        fields=['semester','permit_type']

