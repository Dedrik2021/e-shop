from typing import Any
from django import forms
from .models import Account, UserProfile

class RegistrationForm(forms.ModelForm):
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
    }))
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
        
        
        
    def clean(self):
        clean_data = super(RegistrationForm, self).clean()
        
        password = clean_data.get('password')
        confirm_password = clean_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError('Password does not match')
        
        
        
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone'
        
        self.fields['password'].widget.attrs['placeholder'] = 'Enter Password'
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
            
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')
        
        
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')