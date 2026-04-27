from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, unique=True, verbose_name="Телефон номер")
    is_verified = models.BooleanField(default=False) # SMS тастыкталдыбы
    otp_code = models.CharField(max_length=6, blank=True, null=True) # Убактылуу код

    def __str__(self):
        return self.phone