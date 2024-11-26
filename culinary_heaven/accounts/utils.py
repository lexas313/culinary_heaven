from django.conf import settings
from random import choice
import os


def choosing_avatar(gender):  # Функция для возврата случайного названия аватарки с учетом гендера
    if gender == 'M':
        folder = 'men_avatars'
    else:
        folder = 'women_avatars'

    path = os.path.join(settings.MEDIA_ROOT, f'default_avatars/{folder}')
    avatar_names = [entry.name for entry in os.scandir(path) if entry.is_file()]
    avatar_name = choice(avatar_names)
    avatar_path = os.path.join('default_avatars', folder, avatar_name)
    return avatar_path


def select_random_avatar():  # Функция для возврата случайного названия аватарки
    path = os.path.join(settings.MEDIA_ROOT, f'default_avatars/animal_chefs')
    avatar_names = [entry.name for entry in os.scandir(path) if entry.is_file()]
    if avatar_names:
        avatar_name = choice(avatar_names)
        avatar_path = os.path.join('default_avatars/animal_chefs', avatar_name)
        return avatar_path
    else:
        return ''
