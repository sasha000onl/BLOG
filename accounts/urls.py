from django.urls import path
from accounts import views
from .views import register, user_login, profile, user_logout

app_name = 'accounts'



urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('profile/', profile, name='profile'),
    path('logout/', user_logout, name='logout'),
]