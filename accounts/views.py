from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm, ProfileUpdateForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:profile')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accounts:profile')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('accounts:login')