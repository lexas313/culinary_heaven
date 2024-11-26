from datetime import timedelta

from django import template
from django.db.models import Count, Q
from django.utils import timezone

from recipes.filters import RecipeFilter, BasketRecipeFilter
from recipes.models import Category, Tag, Recipe, CookingMethod, Ingredient, Basket

register = template.Library()


@register.inclusion_tag('recipes/list_categories.html')
def show_categories(cat_selected=0):
    cats = Category.objects.annotate(total=Count('category')).filter(total__gt=0)
    return {'cats': cats, 'cat_selected': cat_selected}


@register.inclusion_tag('recipes/list_tags.html', takes_context=True)
def show_tags(context):
    request = context['request']
    selected_tags = request.GET.getlist('tags_sidebar')

    published_recipes = Recipe.published.all()
    tags = Tag.objects.annotate(
        total=Count('tags', filter=Q(tags__in=published_recipes))
    ).filter(total__gt=0)

    return {
        'tags': tags,
        'selected_tags': selected_tags,
    }


@register.inclusion_tag('recipes/list_filters.html', takes_context=True)
def show_filters(context):
    request = context['request']
    view = context.get('view')

    if view and hasattr(view, 'get_filterset'):
        filterset = view.get_filterset()
    else:
        # Получаем queryset для текущего view
        queryset = view.get_queryset()

        # Проверяем, относится ли queryset к модели Recipe
        if queryset.model == Recipe:
            # Создаем фильтр для модели Recipe
            filterset = RecipeFilter(request.GET or None, queryset=queryset)
            filterset.filters['category'].queryset = Category.objects.filter(category__in=queryset).distinct()
            filterset.filters['tags'].queryset = Tag.objects.filter(tags__in=queryset).distinct()
            filterset.filters['cooking_method'].queryset = CookingMethod.objects.filter(cooking_method__in=queryset).distinct()
        elif queryset.model == Basket:
            # Если модель Basket
            filterset = BasketRecipeFilter(request.GET or None, queryset=queryset)

            filterset.filters['category'].queryset = Category.objects.filter(
                category__in=Recipe.objects.filter(baskets__in=queryset).values('category')
            ).distinct().order_by('name_category')

            filterset.filters['tags'].queryset = Tag.objects.filter(
                tags__in=Recipe.objects.filter(baskets__in=queryset).values('tags')
            ).distinct().order_by('name_tag')

            filterset.filters['cooking_method'].queryset = CookingMethod.objects.filter(
                cooking_method__in=Recipe.objects.filter(baskets__in=queryset).values('cooking_method')
            ).distinct().order_by('name_cooking_method')
        else:
            filterset = None

    return {'filter': filterset}


@register.inclusion_tag('recipes/list_recipe_rating.html')
def show_recipe_rating():
    # Фильтрация рецептов, созданных за последние 7 дней
    one_week_ago = timezone.now() - timedelta(days=7)
    published_recipes = Recipe.published.all().filter(date_of_creation__gt=one_week_ago)

    # Сортировка по рейтингу и выборка 10 записей с максимальным рейтингом
    # week_rating = published_recipes.annotate(average_rating=Avg('ratings__average')).order_by('-average_rating')[:10]
    week_rating = published_recipes.order_by('-ratings__average')[:10]

    return {'week_rating': week_rating}