from uuid import uuid4

from django.http import HttpResponseForbidden
from pytils.translit import slugify
from transliterate import translit
import os

class DataMixin:
    paginate_by = 20
    title_page = None
    cat_selected = None
    extra_context = {}
    check_authorship = False  # По умолчанию проверка авторства не проводится

    def __init__(self):
        if self.title_page:
            self.extra_context['title'] = self.title_page

        if self.cat_selected is not None:
            self.extra_context['cat_selected'] = self.cat_selected

        if self.paginate_by is not None:
            self.extra_context['paginate_by'] = self.paginate_by

    def get_mixin_context(self, context, **kwargs):
        context['cat_selected'] = self.cat_selected if self.cat_selected is not None else None
        context.update(kwargs)
        return context

    def dispatch(self, request, *args, **kwargs):
        if self.check_authorship:
            self.object = self.get_object()
            if self.object.author != request.user:  # Запрещаем изменять или удалять рецепты не авторам
                return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


def unique_slugify(instance, slug):
    """
    Генератор уникальных SLUG для моделей, в случае существования такого SLUG.
    """
    model = instance.__class__
    unique_slug = slugify(slug)
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{unique_slug}-{uuid4().hex[:8]}'
    return unique_slug


def transliterate_image_filename(image_field):
    """
    Транслитерирует полное имя файла изображения без разделения на имя и расширение.

    :param image_field: Поле ImageField объекта модели
    :return: Новое транслитерированное имя файла
    """
    if image_field:
        # Получаем полное имя файла (включая расширение)
        filename = image_field.name

        # Транслитерация имени файла
        transliterated_filename = translit(filename, 'ru', reversed=True)

        # Присвоение нового транслитерированного имени файлу
        return transliterated_filename

    return None