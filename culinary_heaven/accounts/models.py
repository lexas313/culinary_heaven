from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from .utils import choosing_avatar, select_random_avatar


class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=15, blank=True, null=True, default='')
    image_profile = models.ImageField(upload_to="image_profile/%Y/%m/%d/", default=None, null=True, blank=True, verbose_name='Фото профиля ')
    gender = models.CharField(verbose_name='Пол', max_length=1, blank=True, null=True, choices=GENDER_CHOICES)

    def save(self, *args, **kwargs):
        """
        Рандомное присвоение аватарки профилю
        """
        random_avatar = select_random_avatar()
        if not self.image_profile:
            self.image_profile = random_avatar
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.username})
