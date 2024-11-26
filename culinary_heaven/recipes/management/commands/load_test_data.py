from django.core.files import File
from django.core.management import BaseCommand, call_command
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
import os
from recipes.models import Recipe, Tag, CookingMethod, CookingStep
from django.conf import settings

class Command(BaseCommand):
    help = 'Load test data into database'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Loading categories and tags...')
        call_command('loaddata', 'recipes/fixtures/initial_data.json')

        # Привязываем теги к рецепту
        recipe = get_object_or_404(Recipe, pk=1)
        tags = Tag.objects.filter(pk__in=[1, 2])
        recipe.tags.add(*tags)  # Добавляем теги к рецепту

        # Привязываем способы приготовления к рецепту
        cooking_methods = CookingMethod.objects.filter(pk__in=[1, 2, 3])
        recipe.cooking_method.add(*cooking_methods)  # Добавляем способы приготовления к рецепту

        # Устанавливаем текущую дату создания рецепта
        recipe.date_of_creation = timezone.now()
        recipe.save()  # Сохраняем изменения в базе данных

        # После загрузки данных, можно также загрузить изображения
        self.stdout.write('Populating recipes with images...')
        self.populate_images()

    def populate_images(self):
        # Используем BASE_DIR для построения пути
        image_dirs = {
            "dish": os.path.join(settings.BASE_DIR, 'recipes', 'static', 'recipes', 'images', 'initial_images', 'image_ready_dish'),
            "step": os.path.join(settings.BASE_DIR, 'recipes', 'static', 'recipes', 'images', 'initial_images', 'image_step')
        }

        recipe = get_object_or_404(Recipe, pk=1)
        self.load_image(recipe.image_ready_dish, 'eggs.jpg', image_dirs['dish'], recipe.title)

        steps = [
            (1, 'oil.jpg'),
            (2, 'break_eggs.jpeg'),
            (3, 'cover.jpeg')
        ]

        for step_id, image_name in steps:
            cooking_step = get_object_or_404(CookingStep, pk=step_id)
            self.load_image(cooking_step.image_step, image_name, image_dirs['step'], cooking_step.description_step)

    def load_image(self, image_field, image_name, image_dir, description):
        try:
            with open(os.path.join(image_dir, image_name), 'rb') as f:
                image_field.save(image_name, File(f))
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded image for {description}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading image for {description}: {e}'))