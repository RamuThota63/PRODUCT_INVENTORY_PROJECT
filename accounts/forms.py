# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.validators import validate_email

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_picture = forms.ImageField(required=False)
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2', 'profile_picture')
    
    def clean_email(self):
        email = self.cleaned_data['email']
        validate_email(email)
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email