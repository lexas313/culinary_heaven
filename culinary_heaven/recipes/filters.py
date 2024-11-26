import django_filters
from django import forms
from django.db.models import Q
from django_filters import CharFilter, ModelMultipleChoiceFilter
from .models import Recipe, Category, Ingredient, Tag, CookingMethod, Basket
from django.forms import CheckboxSelectMultiple


class RecipeFilter(django_filters.FilterSet):
    search = CharFilter(
        method='filter_by_all_fields',
        label='Поиск')

    category = ModelMultipleChoiceFilter(
        queryset=Category.objects.none(),  # Изначально пустой queryset
        widget=CheckboxSelectMultiple,
        label='Категория'
    )

    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.none(),  # Изначально пустой queryset
        widget=CheckboxSelectMultiple,
        label='Теги'
    )

    cooking_method = ModelMultipleChoiceFilter(
        queryset=CookingMethod.objects.none(),  # Изначально пустой queryset
        widget=CheckboxSelectMultiple,
        label='Способ приготовления'
    )

    contains_ingredients = CharFilter(
        method='filter_by_contains_ingredients',
        label='Ингредиенты в составе',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите ингредиенты через запятую',
        })
    )

    exclude_ingredients = CharFilter(
        method='filter_by_exclude_ingredients',
        label='Исключить ингредиенты',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите ингредиенты через запятую',
        })
    )

    class Meta:
        model = Recipe
        fields = ['search', 'category', 'tags', 'cooking_method', 'contains_ingredients', 'exclude_ingredients']

    def __init__(self, *args, **kwargs):
        queryset = kwargs.get('queryset', Recipe.objects.none())
        super().__init__(*args, **kwargs)

        # Получаем связанные объекты на основе переданного queryset
        self.filters['category'].queryset = Category.objects.filter(category__in=queryset).distinct().order_by('name_category')
        self.filters['tags'].queryset = Tag.objects.filter(tags__in=queryset).distinct().order_by('name_tag')
        self.filters['cooking_method'].queryset = CookingMethod.objects.filter(cooking_method__in=queryset).distinct().order_by('name_cooking_method')

        for filter in self.filters.values():
            if isinstance(filter.field.widget, forms.TextInput):
                filter.field.widget.attrs.update({'class': 'form-fields'})

    def filter_by_all_fields(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )

    def filter_by_contains_ingredients(self, queryset, name, value):
        # Разбираем строку ингредиентов на список и преобразуем в нижний регистр
        ingredient_names_lower = [name.strip().lower() for name in value.split(',') if name.strip()]
        ingredient_names_title = [name.title() for name in ingredient_names_lower]
        ingredient_names_upper = [name.upper() for name in ingredient_names_lower]
        ingredient_names = ingredient_names_lower + ingredient_names_title + ingredient_names_upper

        # Фильтруем рецепты, содержащие все указанные ингредиенты
        if ingredient_names:
            ingredient_ids = Ingredient.objects.filter(name_ingredient__in=ingredient_names).values_list('id',
                                                                                                         flat=True)
            return queryset.filter(recipe_ingredient__in=ingredient_ids).distinct()
        return queryset

    def filter_by_exclude_ingredients(self, queryset, name, value):
        # Разбираем строку ингредиентов на список и преобразуем в нижний регистр
        ingredient_names_lower = [name.strip().lower() for name in value.split(',') if name.strip()]
        ingredient_names_title = [name.title() for name in ingredient_names_lower]
        ingredient_names_upper = [name.upper() for name in ingredient_names_lower]
        ingredient_names = ingredient_names_lower + ingredient_names_title + ingredient_names_upper

        # Фильтруем рецепты, содержащие все указанные ингредиенты
        if ingredient_names:
            ingredient_ids = Ingredient.objects.filter(name_ingredient__in=ingredient_names).values_list('id',
                                                                                                         flat=True)
            return queryset.exclude(recipe_ingredient__in=ingredient_ids).distinct()
        return queryset


class BasketRecipeFilter(django_filters.FilterSet):
    search = CharFilter(
        method='filter_by_all_fields',
        label='Поиск'
    )

    category = ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        widget=CheckboxSelectMultiple,
        label='Категория',
        field_name='recipe__category'  # Используем путь через recipe
    )

    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        widget=CheckboxSelectMultiple,
        label='Теги',
        field_name='recipe__tags'  # Используем путь через recipe
    )

    cooking_method = ModelMultipleChoiceFilter(
        queryset=CookingMethod.objects.all(),
        widget=CheckboxSelectMultiple,
        label='Способ приготовления',
        field_name='recipe__cooking_method'  # Используем путь через recipe
    )

    contains_ingredients = CharFilter(method='filter_by_contains_ingredients', label='Ингредиенты в составе')
    exclude_ingredients = CharFilter(method='filter_by_exclude_ingredients', label='Исключить ингредиенты')

    class Meta:
        model = Basket
        fields = ['search', 'category', 'tags', 'cooking_method', 'contains_ingredients', 'exclude_ingredients']

    def __init__(self, *args, **kwargs):
        queryset = kwargs.get('queryset', Basket.objects.none())
        super().__init__(*args, **kwargs)

        # Фильтрация категорий, тегов и способов приготовления на основе корзины пользователя
        self.filters['category'].queryset = Category.objects.filter(
            id__in=Recipe.objects.filter(baskets__in=queryset).values_list('category_id', flat=True)
        ).distinct().order_by('name_category')

        self.filters['tags'].queryset = Tag.objects.filter(
            id__in=Recipe.objects.filter(baskets__in=queryset).values_list('tags__id', flat=True)
        ).distinct().order_by('name_tag')

        self.filters['cooking_method'].queryset = CookingMethod.objects.filter(
            id__in=Recipe.objects.filter(baskets__in=queryset).values_list('cooking_method__id', flat=True)
        ).distinct().order_by('name_cooking_method')

        # Настройка класса для текстовых полей
        for filter in self.filters.values():
            if isinstance(filter.field.widget, forms.TextInput):
                filter.field.widget.attrs.update({'class': 'form-fields'})

    def filter_by_all_fields(self, queryset, name, value):
        # Фильтрация по полям модели Recipe через связь ForeignKey
        return queryset.filter(
            Q(recipe__title__icontains=value) |
            Q(recipe__description__icontains=value)
        )

    def filter_by_contains_ingredients(self, queryset, name, value):
        # Фильтруем рецепты по ингредиентам, используя связь ForeignKey
        ingredient_names_lower = [name.strip().lower() for name in value.split(',') if name.strip()]
        ingredient_names_title = [name.title() for name in ingredient_names_lower]
        ingredient_names_upper = [name.upper() for name in ingredient_names_lower]
        ingredient_names = ingredient_names_lower + ingredient_names_title + ingredient_names_upper

        if ingredient_names:
            ingredient_ids = Ingredient.objects.filter(name_ingredient__in=ingredient_names).values_list('id', flat=True)
            return queryset.filter(recipe__recipe_ingredient__in=ingredient_ids).distinct()
        return queryset

    def filter_by_exclude_ingredients(self, queryset, name, value):
        # Фильтруем рецепты по ингредиентам, используя связь ForeignKey
        ingredient_names_lower = [name.strip().lower() for name in value.split(',') if name.strip()]
        ingredient_names_title = [name.title() for name in ingredient_names_lower]
        ingredient_names_upper = [name.upper() for name in ingredient_names_lower]
        ingredient_names = ingredient_names_lower + ingredient_names_title + ingredient_names_upper

        if ingredient_names:
            ingredient_ids = Ingredient.objects.filter(name_ingredient__in=ingredient_names).values_list('id', flat=True)
            return queryset.exclude(recipe__recipe_ingredient__in=ingredient_ids).distinct()
        return queryset