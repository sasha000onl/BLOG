from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):

    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def is_moderator(self):
        return self.groups.filter(name='Moderators').exists()

    def is_administrator(self):
        return self.groups.filter(name='Administrators').exists() or self.is_superuser

# Якщо потрібно окрема модель профілю (альтернатива, якщо не хочете розширювати User)
# class Profile(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     bio = models.TextField(blank=True)
#     # Інші поля