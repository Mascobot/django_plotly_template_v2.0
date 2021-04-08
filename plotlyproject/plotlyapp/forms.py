from django import forms 
from django.core import validators


class LoginForm(forms.Form):
    Email = forms.EmailField(widget=forms.TextInput)#The name of the "Email" variable needs to match with the "name=" variable in the input filed in the html template
    pwd = forms.CharField(max_length=32, widget=forms.PasswordInput)#The name of the "pwd" variable needs to match with the "name=" variable in the input filed in the html template
    botcatcher = forms.CharField(required=False, widget=forms.HiddenInput,
                                validators=[validators.MaxLengthValidator(0)])
                            

class RegisterForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput)
    last_name = forms.CharField(widget=forms.TextInput)
    Company = forms.CharField(required=False, widget=forms.TextInput)
    Email = forms.EmailField(widget=forms.TextInput)
    pwd = forms.CharField(max_length=32, widget=forms.PasswordInput)
    verify_pwd = forms.CharField(max_length=32, widget=forms.PasswordInput)
    botcatcher = forms.CharField(required=False, widget=forms.HiddenInput,
                                validators=[validators.MaxLengthValidator(0)])
                            
class RecoveryForm(forms.Form):
    Email = forms.EmailField(widget=forms.TextInput)
    botcatcher = forms.CharField(required=False, widget=forms.HiddenInput,
                                validators=[validators.MaxLengthValidator(0)])
    
