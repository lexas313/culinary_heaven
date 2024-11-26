from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.urls import reverse
from star_ratings.models import Rating
from accounts.models import User
from .utils import unique_slugify, transliterate_image_filename
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone


class PublishedManager(models.Manager):
    """
    Менеджер для опубликованных рецептов
    """

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(is_published=Recipe.Status.PUBLISHED) & Q(status_moderation=Recipe.StatusModeration.APPROVED)
        )

    def for_user(self, user):
        """
        Метод возвращающий все рецепты автора
        """
        if user.is_authenticated:
            return super().get_queryset().filter(
                (Q(is_published=Recipe.Status.PUBLISHED) & Q(status_moderation=Recipe.StatusModeration.APPROVED)) | Q(
                    author=user)
            )
        else:
            return self.get_queryset()


class Recipe(models.Model):  # Рецепт
    class Status(models.IntegerChoices):
        PUBLISHED = 1, 'Опубликовано'
        DRAFT = 0, 'Черновик'

    class StatusModeration(models.IntegerChoices):
        MODERATION = 0, 'На модерации'
        APPROVED = 1, 'Одобрено'
        REJECTED = 2, 'Отклонено'

    status_moderation = models.IntegerField(choices=StatusModeration.choices, default=StatusModeration.MODERATION,
                                            verbose_name="Статус модерации", null=True, blank=True)
    moderation_feedback = models.TextField(verbose_name='Причина отклонения', null=True, blank=True)

    date_of_creation = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True)
    date_of_update = models.DateTimeField(auto_now=True, verbose_name="Дата изменения", null=True)
    is_published = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                       default=Status.PUBLISHED, verbose_name="Статус")
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, verbose_name='Категория',
                                 related_name='category')
    tags = models.ManyToManyField('Tag', blank=True, verbose_name='Теги', related_name='tags')
    slug = models.CharField(max_length=255, verbose_name='URL-название')
    cooking_method = models.ManyToManyField('CookingMethod', blank=True, verbose_name='Способ приготовления', related_name='cooking_method')
    description = models.TextField(max_length=1200, verbose_name='Описание')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Автор', blank=True)
    cooking_time = models.IntegerField(verbose_name='Время приготовления', null=True, blank=True)
    portions = models.PositiveIntegerField(default=1, verbose_name='Количество порций', null=True, blank=True)
    image_ready_dish = models.ImageField(upload_to="ready_meals/%Y/%m/%d/", default=None, null=True, blank=True,
                                         verbose_name='Фото блюда ')

    ratings = GenericRelation(Rating, related_query_name='recipes')

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'
        ordering = ['-date_of_creation']

    def get_absolute_url(self):
        return reverse('recipes:detail_recipe', kwargs={'slug': self.slug})

    def __str__(self):
        return f'Id:{self.id} {self.title}'

    def save(self, *args, **kwargs):
        # Используем функцию для транслитерации имени файла изображения
        new_filename = transliterate_image_filename(self.image_ready_dish)
        if new_filename:
            self.image_ready_dish.name = new_filename

        # Автоматическая генерация slug'а, если он не был задан
        if not self.slug:
            self.slug = unique_slugify(self, self.title)

        super().save(*args, **kwargs)


class Category(models.Model):  # Категории
    name_category = models.CharField(max_length=255, db_index=True, verbose_name='Категория')
    slug = models.CharField(max_length=255, db_index=True, verbose_name='URL-название', null=True)

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name_category

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели, при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.name_category)
        super().save(*args, **kwargs)


class Tag(models.Model):  # Теги
    name_tag = models.CharField(max_length=255, verbose_name='Тег')
    slug = models.CharField(max_length=255, verbose_name='URL-название', null=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name_tag

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели, при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.name_tag)
        super().save(*args, **kwargs)


class CookingMethod(models.Model):  # Способ приготовления
    name_cooking_method = models.CharField(max_length=255, verbose_name='Способ приготовления')
    slug = models.CharField(max_length=255, verbose_name='URL-название', null=True)

    class Meta:
        verbose_name = 'Способ приготовления'
        verbose_name_plural = 'Способ приготовления'

    def __str__(self):
        return self.name_cooking_method

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели, при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.name_cooking_method)
        super().save(*args, **kwargs)


class Unit(models.Model):  # Единицы измерения ингредиентов
    name_unit = models.CharField(max_length=100, verbose_name='Мера')

    class Meta:
        verbose_name = 'Ед. измерения'
        verbose_name_plural = 'Ед. измерения'

    def __str__(self):
        return self.name_unit


class Ingredient(models.Model):
    recipe_ingredient = models.ForeignKey('Recipe', on_delete=models.CASCADE, verbose_name='Ингредиенты',
                                          related_name='recipe_ingredient')
    name_ingredient = models.CharField(max_length=100, verbose_name='Ингредиент', db_index=True)  # Индексируем поле
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, verbose_name='Мера', related_name='unit')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name_ingredient


class CookingStep(models.Model):  # Шаги приготовления
    recipe_cooking_step = models.ForeignKey('Recipe', on_delete=models.CASCADE, verbose_name='Шаги приготовления',
                                            related_name='recipe_cooking_step')
    description_step = models.TextField(max_length=255, verbose_name='Описание шага')
    image_step = models.ImageField(upload_to="images_step/%Y/%m/%d/", default=None, null=True, blank=True,
                                   verbose_name='Фото шага')

    class Meta:
        verbose_name = 'Шаг приготовления'
        verbose_name_plural = 'Шаги приготовления'

    def __str__(self):
        return self.description_step

    def save(self, *args, **kwargs):
        # Используем функцию для транслитерации имени файла изображения
        new_filename = transliterate_image_filename(self.image_step)
        if new_filename:
            self.image_step.name = new_filename

        super().save(*args, **kwargs)


class Favorite(models.Model):  # Избранное
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)  # default=timezone.now

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return self.recipe


class Like(models.Model):  # Лайки
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)  # default=timezone.now


class Comment(MPTTModel):
    """
    Модель древовидных комментариев
    """

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Статья', related_name='comments')
    # Автор комментария (пользователь) если авторизован
    author = models.ForeignKey(User, verbose_name='Автор комментария', on_delete=models.CASCADE,
                               related_name='comments_author', null=True, blank=True)
    # Гости сайта, если неавторизованные
    name = models.CharField(max_length=255, verbose_name='Имя посетителя', blank=True)
    email = models.EmailField(max_length=255, verbose_name='Email посетителя', blank=True)
    # Прочие поля
    content = models.TextField(verbose_name='Текст комментария', max_length=3000)
    time_create = models.DateTimeField(verbose_name='Время добавления', auto_now_add=True)
    time_update = models.DateTimeField(verbose_name='Время обновления', auto_now=True)
    status = models.CharField(choices=STATUS_OPTIONS, default='published', verbose_name='Статус поста', max_length=10)
    parent = TreeForeignKey('self', verbose_name='Родительский комментарий', null=True, blank=True,
                            related_name='children', on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class MTTMeta:
        order_insertion_by = ('-time_create',)

    class Meta:
        db_table = 'app_comments'
        indexes = [models.Index(fields=['-time_create', 'time_update', 'status', 'parent'])]
        ordering = ['-time_create']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        if self.author:
            return f'{self.author}:{self.content}'
        else:
            return f'{self.name} ({self.email}):{self.content}'

    @property
    def get_avatar(self):
        if self.author:
            return self.author.image_profile.url
        return f'https://ui-avatars.com/api/?size=190&background=random&name={self.name}'


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, verbose_name='Рецепты', related_name='baskets')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')

    def __str__(self):
        return f'{self.user}|{self.recipe.title}'

    def increase_quantity(self):
        self.quantity += 1
        self.save()

    def decrease_quantity(self):
        self.quantity -= 1
        self.save()


class BasketIngredient(models.Model):
    basket = models.ForeignKey('Basket', on_delete=models.CASCADE, verbose_name='Корзина',
                               related_name='basket_ingredients')
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, verbose_name='Ингредиент')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
    unit = models.ForeignKey('Unit', on_delete=models.SET_NULL, null=True, verbose_name='Мера')

    def __str__(self):
        return f'{self.ingredient.name_ingredient} - {self.quantity} {self.unit}'

    def increase_ingredient(self, amount):
        # Добавление количества ингредиентов
        self.quantity += amount
        self.save()

    def decrease_ingredient(self, amount):
        # Удаление количества ингредиентов
        self.quantity -= amount
        if self.quantity <= 0:
            self.delete()  # Удаляем ингредиент, если его количество стало нулевым или отрицательным
        else:
            self.save()
