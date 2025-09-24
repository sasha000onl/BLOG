from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text='',  # або власний help_text
    )
    email = forms.EmailField(
        required=True,
        help_text=""
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        help_text=''  # або власний
    )
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'bio', 'profile_picture')

class LoginForm(AuthenticationForm):
    pass  # Можна кастомізувати, якщо потрібно

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'bio', 'profile_picture')  # Поля для редагування профілю