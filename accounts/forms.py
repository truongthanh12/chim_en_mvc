from django import forms
from django.forms import ModelForm, Textarea, TextInput, PasswordInput
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm
from .models import User
from cart.models import Address


class RegisterForm(UserCreationForm):
    error_css_class = "text-danger"

    class Meta:
        model = User
        fields = ('username', 'email',  'password1', 'password2')

        widgets = {
            'username': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': PasswordInput(attrs={'class': 'form-control'}),
        }


class LoginForm(forms.Form):
    username = forms.CharField(label="User name", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your usename'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name',
                  'last_name', 'mobile', 'city', 'district', 'address')
        widgets = {
            'username': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
        }


class AddressChangeForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('city', 'districts',
                  'address')
        widgets = {
            'address': TextInput(attrs={'class': 'form-control'})
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    error_css_class = "text-danger"
    pass


class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': "Your email"
    }))


class ChangeEmailForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email',)
