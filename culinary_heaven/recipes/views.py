import json
from _pydecimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import OuterRef, Exists, Q
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django_filters.views import FilterView
from .filters import RecipeFilter, BasketRecipeFilter
from .forms import RecipeForm, IngredientsForm, CookingStepForm, CommentCreateForm
from .models import Recipe, Ingredient, Tag, CookingStep, Favorite, Like, Comment, Basket, BasketIngredient
from .utils import DataMixin
from django.utils import formats
from django.core.exceptions import PermissionDenied


class AllRecipeView(DataMixin, FilterView):
    template_name = 'recipes/all_recipes.html'
    filterset_class = RecipeFilter
    cat_selected = 0
    title_page = 'Рецепты'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            favorites = Favorite.objects.filter(user=user, recipe=OuterRef('pk'))
            baskets = Basket.objects.filter(user=user, recipe=OuterRef('pk'))
            recipes = Recipe.published.all().select_related('category').annotate(
                is_favorite=Exists(favorites),
                is_basket=Exists(baskets)
            )

        else:
            recipes = Recipe.published.all().select_related('category')

        return recipes

    def get_filterset(self, filterset_class=None):
        # Получаем текущий отфильтрованный queryset
        queryset = self.get_queryset()

        # Создаём filterset, чтобы применить начальные фильтры
        filterset = self.filterset_class(self.request.GET, queryset=queryset, request=self.request)

        # Пересоздаем queryset на основе уже применённых фильтров
        queryset = filterset.qs

        # Теперь передаем обновленный queryset в filterset, чтобы обновить доступные значения в других фильтрах
        return self.filterset_class(
            self.request.GET or None,
            queryset=queryset,
            request=self.request
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        title_page = self.title_page
        return self.get_mixin_context(context, title=title_page)


class DetailRecipeView(DataMixin, DetailView):
    model = Recipe
    template_name = 'recipes/detail_recipe.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentCreateForm

        # Получаем объект рецепта
        recipe = self.get_object()

        if self.request.user.is_authenticated:
            context['in_basket'] = Basket.objects.filter(user=self.request.user, recipe=recipe).exists()
            context['in_favorite'] = Favorite.objects.filter(user=self.request.user, recipe=recipe).exists()

        # Добавляем заголовок в контекст
        return self.get_mixin_context(context, title=recipe.title)

    def get_object(self, queryset=None):
        recipe = get_object_or_404(Recipe.objects, slug=self.kwargs['slug'])

        # Разрешен просмотр всех рецептов модераторам ('moderator')
        if self.request.user.groups.filter(name='moderator').exists():
            return recipe

        # Проверяем, если рецепт в черновике или модерация не одобрена и текущий пользователь не автор, возвращаем 404
        if (not recipe.is_published or recipe.status_moderation != recipe.StatusModeration.APPROVED) and recipe.author != self.request.user:
            raise Http404("Этот рецепт не опубликован.")

        return recipe


class AddRecipeView(LoginRequiredMixin, DataMixin, CreateView):
    model = Recipe
    template_name = 'recipes/add_recipe.html'
    form_class = RecipeForm
    success_url = reverse_lazy('recipes:all_recipes')
    title_page = 'Создание рецепта'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        IngredientFormSet = inlineformset_factory(Recipe, Ingredient, form=IngredientsForm, can_delete=False, extra=1)
        CookingStepFormSet = inlineformset_factory(Recipe, CookingStep, form=CookingStepForm, can_delete=False, extra=1)
        if self.request.POST:
            context['ingredient_form'] = IngredientFormSet(self.request.POST)
            context['cooking_step_form'] = CookingStepFormSet(self.request.POST, self.request.FILES)
        else:
            context['ingredient_form'] = IngredientFormSet()
            context['cooking_step_form'] = CookingStepFormSet()
        return self.get_mixin_context(context)

    def form_valid(self, form):
        context = self.get_context_data()
        ingredient_form = context['ingredient_form']
        cooking_step_form = context['cooking_step_form']
        if ingredient_form.is_valid() and cooking_step_form.is_valid():
            form.instance.author = self.request.user  # Установка автора рецепта
            self.object = form.save()
            ingredient_form.instance = self.object
            ingredient_form.save()

            cooking_step_form.instance = self.object
            cooking_step_form.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class UpdateRecipeView(DataMixin, UpdateView):
    model = Recipe
    template_name = 'recipes/update_recipe.html'
    form_class = RecipeForm
    success_url = reverse_lazy('recipes:all_recipes')
    title_page = 'Редактирование рецепта'
    check_authorship = True  # Включаем проверку авторства для этого представления

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        IngredientFormSet = inlineformset_factory(Recipe, Ingredient, form=IngredientsForm, can_delete=True, extra=0)
        CookingStepFormSet = inlineformset_factory(Recipe, CookingStep, form=CookingStepForm, can_delete=True, extra=0)
        if self.request.POST:
            context['ingredient_form'] = IngredientFormSet(self.request.POST, instance=self.object)
            context['cooking_step_form'] = CookingStepFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['ingredient_form'] = IngredientFormSet(instance=self.object)
            context['cooking_step_form'] = CookingStepFormSet(instance=self.object)
        return self.get_mixin_context(context)

    def form_valid(self, form):
        context = self.get_context_data()
        ingredient_form = context['ingredient_form']
        cooking_step_form = context['cooking_step_form']
        if ingredient_form.is_valid() and cooking_step_form.is_valid():
            self.object = form.save(commit=False)
            self.object.status_moderation = Recipe.StatusModeration.MODERATION
            self.object.save()
            form.save_m2m()
            ingredient_form.save()
            cooking_step_form.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DeleteRecipeView(DataMixin, DeleteView):
    model = Recipe
    template_name = 'recipes/confirm_delete.html'
    success_url = reverse_lazy('recipes:all_recipes')
    title_page = 'Удаление рецепта'
    check_authorship = True  # Включаем проверку авторства для этого представления


class RecipeCategory(DataMixin, FilterView):
    template_name = 'recipes/all_recipes.html'
    allow_empty = False
    filterset_class = RecipeFilter

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            favorites = Favorite.objects.filter(user=user, recipe=OuterRef('pk'))
            baskets = Basket.objects.filter(user=user, recipe=OuterRef('pk'))
            recipes = Recipe.published.filter(category__slug=self.kwargs['slug']).select_related('category').annotate(
                is_favorite=Exists(favorites),
                is_basket=Exists(baskets)
            )

        else:
            recipes = Recipe.published.filter(category__slug=self.kwargs['slug']).select_related('category')

        return recipes

    def get_filterset(self, filterset_class=None):
        # Получаем текущий отфильтрованный queryset
        queryset = self.get_queryset()

        # Создаём filterset, чтобы применить начальные фильтры
        filterset = self.filterset_class(self.request.GET, queryset=queryset, request=self.request)

        # Пересоздаем queryset на основе уже применённых фильтров
        queryset = filterset.qs

        # Теперь передаем обновленный queryset в filterset, чтобы обновить доступные значения в других фильтрах
        return self.filterset_class(
            self.request.GET or None,
            queryset=queryset,
            request=self.request
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = context['object_list'][0].category
        return self.get_mixin_context(context, title=cat.name_category, cat_selected=cat.pk)


class RecipeTag(DataMixin, FilterView):
    template_name = 'recipes/all_recipes.html'
    allow_empty = False
    title_page = 'Рецепты'
    filterset_class = RecipeFilter

    def get(self, request, *args, **kwargs):
        selected_tags = request.GET.getlist('tags_sidebar')
        if not selected_tags:
            # Если теги не выбраны, перенаправляем на представление AllRecipeView
            return redirect('recipes:all_recipes')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            favorites = Favorite.objects.filter(user=user, recipe=OuterRef('pk'))
            baskets = Basket.objects.filter(user=user, recipe=OuterRef('pk'))
            recipes = Recipe.published.all().select_related('category').annotate(
                is_favorite=Exists(favorites),
                is_basket=Exists(baskets)
            )

        else:
            recipes = Recipe.published.all().select_related('category')

        # Фильтрация по тегам
        selected_tags = self.request.GET.getlist('tags_sidebar')

        if selected_tags:
            recipes = recipes.filter(tags__slug__in=selected_tags).distinct()
            # Формируем строку из имен тегов для заголовка
            tag_names = [tag.name_tag for tag in Tag.objects.filter(slug__in=selected_tags)]
            self.title_page = ', '.join(tag_names)

        return recipes

    def get_filterset(self, filterset_class=None):
        # Получаем текущий отфильтрованный queryset
        queryset = self.get_queryset()

        # Создаём filterset, чтобы применить начальные фильтры
        filterset = self.filterset_class(self.request.GET, queryset=queryset, request=self.request)

        # Пересоздаем queryset на основе уже применённых фильтров
        queryset = filterset.qs

        # Теперь передаем обновленный queryset в filterset, чтобы обновить доступные значения в других фильтрах
        return self.filterset_class(
            self.request.GET or None,
            queryset=queryset,
            request=self.request
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=self.title_page)


class RecipeFavorite(LoginRequiredMixin, DataMixin, FilterView):
    template_name = 'recipes/favorite.html'
    title_page = 'Избранные'
    filterset_class = RecipeFilter
    paginate_by = None

    def get_queryset(self):
        # Получаем текущего пользователя
        user = self.request.user
        # Возвращаем QuerySet избранных рецептов для пользователя
        return Recipe.objects.filter(favorite__user=user).select_related('category').distinct()

    def get_filterset(self, filterset_class=None):
        # Получаем текущий отфильтрованный queryset
        queryset = self.get_queryset()

        # Создаём filterset, чтобы применить начальные фильтры
        filterset = self.filterset_class(self.request.GET, queryset=queryset, request=self.request)

        # Пересоздаем queryset на основе уже применённых фильтров
        queryset = filterset.qs

        # Теперь передаем обновленный queryset в filterset, чтобы обновить доступные значения в других фильтрах
        return self.filterset_class(
            self.request.GET or None,
            queryset=queryset,
            request=self.request
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cat_selected'] = None
        return context


class AddToFavoritesView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        recipe_id = request.POST.get('recipe_id')
        recipe = Recipe.objects.get(id=recipe_id)

        favorite, created = Favorite.objects.get_or_create(user=user, recipe=recipe)

        if not created:
            # Если уже в избранном, удаляем его
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True

        context = {
            'favorite_count': recipe.favorite_set.count(),
            'is_favorite': is_favorite,
            'status': 'success',
        }
        return JsonResponse(context)


# class LikeView(View):
#     def post(self, request, *args, **kwargs):
#         user = request.user
#         recipe_id = request.POST.get('recipe_id')
#         recipe = Recipe.objects.get(id=recipe_id)
#
#         like, created = Like.objects.get_or_create(user=user, recipe=recipe)
#
#         if not created:
#             # Лайк уже существует, удаляем его
#             like.delete()
#             is_liked = False
#         else:
#             is_liked = True
#
#         context = {
#             'like_count': recipe.like_set.count(),
#             'is_liked': is_liked,
#             'status': 'success',
#         }
#         return JsonResponse(context)


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentCreateForm

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.recipe_id = self.kwargs.get('pk')

        if self.request.user.is_authenticated:
            comment.author = self.request.user
            comment.name = self.request.user.username
            comment.email = self.request.user.email
        else:
            # # Возможность неавторизованным пользователям оставлять комментарии
            # comment.name = form.cleaned_data.get('name')
            # comment.email = form.cleaned_data.get('email')

            # Перенаправление неавторизованных пользователей на страницу входа
            login_url = reverse_lazy('accounts:login')
            return redirect(f'{login_url}?next={self.request.path}')

        comment.ip_address = self.request.META.get('REMOTE_ADDR')
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()
        comment_count = Comment.objects.filter(recipe_id=self.kwargs.get('pk')).count()
        recipe_slug = comment.recipe.slug

        if self.is_ajax():
            if self.request.user.is_authenticated:
                data = {
                    'is_child': comment.is_child_node(),
                    'id': comment.id,
                    'author': comment.author.username,
                    'parent_id': comment.parent_id,
                    'time_create': formats.date_format(comment.time_create, "DATETIME_FORMAT"),
                    'avatar': comment.get_avatar,
                    'content': comment.content,
                    'get_absolute_url': comment.author.get_absolute_url(),
                    'comment_count': comment_count,
                }
            else:
                data = {
                    'is_child': comment.is_child_node(),
                    'id': comment.id,
                    'author': comment.name,
                    'parent_id': comment.parent_id,
                    'time_create': formats.date_format(comment.time_create, "DATETIME_FORMAT"),
                    'avatar': comment.get_avatar,
                    'content': comment.content,
                    'get_absolute_url': f'mailto:{comment.email}',
                    'comment_count': comment_count,
                }
            return JsonResponse(data, status=200)
        return redirect('recipes:detail_recipe', slug=recipe_slug)

    def form_invalid(self, form):
        # Обработка ошибки валидации
        if self.is_ajax():
            errors = form.errors.as_json()
            return JsonResponse({'errors': 'Некорректные данные'}, status=400)
        return super().form_invalid(form)


class CommentDeleteView(View):
    def post(self, request, *args, **kwargs):
        comment_id = request.POST.get('comment_id')
        comment = Comment.objects.get(id=comment_id)
        # Убедитесь, что пользователь, запрашивающий удаление, является автором или имеет разрешение.
        if request.user == comment.author or request.user.is_superuser:
            comment.delete()
            comment_count = Comment.objects.filter(recipe_id=comment.recipe_id).count()
            return JsonResponse({'status': 'success',
                                 'comment_count': comment_count
                                 }, status=200)
        else:
            return JsonResponse({'status': 'error'}, status=403)


class BasketView(LoginRequiredMixin, DataMixin, FilterView):
    template_name = 'recipes/basket.html'
    title_page = 'Корзина'
    filterset_class = BasketRecipeFilter
    paginate_by = None

    def get_queryset(self):
        recipes = Basket.objects.filter(user=self.request.user).select_related('recipe')

        return recipes

        # return Recipe.objects.filter(baskets__user=self.request.user).select_related('category').distinct()

    def get_filterset(self, filterset_class=None):
        # Получаем текущий отфильтрованный queryset
        queryset = self.get_queryset()

        # Создаём filterset, чтобы применить начальные фильтры
        filterset = self.filterset_class(self.request.GET, queryset=queryset, request=self.request)

        # Пересоздаем queryset на основе уже применённых фильтров
        queryset = filterset.qs

        # Теперь передаем обновленный queryset в filterset, чтобы обновить доступные значения в других фильтрах
        return self.filterset_class(
            self.request.GET or None,
            queryset=queryset,
            request=self.request
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cat_selected'] = None

        return context


class AddBasketView(View):
    def post(self, request, *args, **kwargs):
        recipe_id = request.POST.get('recipe_id')
        recipe = Recipe.published.get(id=recipe_id)
        user_basket, created = Basket.objects.get_or_create(user=request.user, recipe=recipe)

        if created:
            # Рецепт не был в корзине, добавляем ингредиенты
            for ingredient in recipe.recipe_ingredient.all():
                BasketIngredient.objects.create(
                    basket=user_basket,
                    ingredient=ingredient,
                    quantity=ingredient.amount,
                    unit=ingredient.unit
                )
            return JsonResponse({'status': 'success', 'message': 'Рецепт добавлен в корзину'})
        else:
            # Рецепт уже в корзине, удаляем его
            user_basket.delete()
            return JsonResponse({'status': 'success', 'message': 'Рецепт удален из корзины'})


class DeleteBasketItemView(View):
    def post(self, request, *args, **kwargs):
        basket_id = request.POST.get('basket_id')
        basket = get_object_or_404(Basket, id=basket_id)
        basket.delete()
        return JsonResponse({'status': 'deleted'})


class IncreaseQuantityView(View):
    def post(self, request, *args, **kwargs):
        basket_id = request.POST.get('basket_id')
        basket = get_object_or_404(Basket, id=basket_id)
        basket.increase_quantity()

        # Увеличиваем количество ингредиентов
        for basket_ingredient in basket.basket_ingredients.all():
            basket_ingredient.increase_ingredient(basket_ingredient.ingredient.amount)

        return JsonResponse({'status': 'success', 'quantity': basket.quantity})


class DecreaseQuantityView(View):
    def post(self, request, *args, **kwargs):
        basket_id = request.POST.get('basket_id')
        basket = get_object_or_404(Basket, id=basket_id)
        basket.decrease_quantity()

        # Уменьшаем количество ингредиентов
        for basket_ingredient in basket.basket_ingredients.all():
            basket_ingredient.decrease_ingredient(basket_ingredient.ingredient.amount)

        # Проверка, не стало ли количество равным нулю или меньше
        if basket.quantity <= 0:
            basket.delete()  # Удаление товара из корзины
            return JsonResponse({'status': 'deleted'})
        else:
            basket.save()  # Сохранение обновленного количества товара
            return JsonResponse({'status': 'success', 'quantity': basket.quantity})


# Очистить корзину
class DeleteBasketView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        Basket.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True})


# Удалить ингредиент из корзины
class DeleteIngredientView(View):
    def post(self, request, *args, **kwargs):
        basket_ingredient_id = request.POST.get('basket_ingredient_id')
        basket_ingredient = get_object_or_404(BasketIngredient, id=basket_ingredient_id)
        basket = basket_ingredient.basket
        basket_ingredient.delete()

        # Проверяем, остались ли ингредиенты в корзине
        ingredients_left = basket.basket_ingredients.exists()

        # Если ингредиентов не осталось, отправляем флаг
        return JsonResponse({
            'success': True,
            'ingredients_left': ingredients_left
        })


class UpdateBasketIngredient(View):
    def post(self, request, *args, **kwargs):
        # Получаем все корзины текущего пользователя
        baskets = Basket.objects.filter(user=request.user)

        # Обновляем количество каждого ингредиента в каждой корзине
        for basket in baskets:
            for recipe_ingredient in basket.recipe.recipe_ingredient.all():
                obj, created = BasketIngredient.objects.get_or_create(
                    basket=basket,
                    ingredient=recipe_ingredient,
                    defaults={
                        'quantity': recipe_ingredient.amount * basket.quantity,
                        'unit': recipe_ingredient.unit
                    }
                )
                if not created:
                    # Если объект уже существует, обновляем количество
                    obj.quantity = recipe_ingredient.amount * basket.quantity
                    obj.save()

        return JsonResponse({'status': 'success', 'message': 'Корзина обновлена'})


class ConvertUnitView(View):
    units = {
        'гр': {'кг': Decimal('0.001'), 'ч.л.': Decimal('0.25'), 'ст.л.': Decimal('0.04'), 'стакан': Decimal('0.005')},
        'кг': {'гр': Decimal('1000'), 'ч.л.': Decimal('250'), 'ст.л.': Decimal('40'), 'стакан': Decimal('5')},
        'мл': {'л': Decimal('0.001'), 'ч.л.': Decimal('0.25'), 'ст.л.': Decimal('0.04'), 'стакан': Decimal('0.004')},
        'л': {'мл': Decimal('1000'), 'ч.л.': Decimal('250'), 'ст.л.': Decimal('40'), 'стакан': Decimal('4')},
        'ч.л.': {'гр': Decimal('4'), 'мл': Decimal('4'), 'ст.л.': Decimal('0.16')},
        'ст.л.': {'гр': Decimal('25'), 'мл': Decimal('25'), 'ч.л.': Decimal('6.25')},
        'стакан': {'гр': Decimal('200'), 'мл': Decimal('250')},
    }

    def get_possible_units(self, old_unit):
        if old_unit in self.units:
            return list(self.units[old_unit].keys())
        else:
            return []

    def conversion_ingredient(self, amount, old_unit, new_unit):
        # Преобразуем строку в число, заменив запятую на точку
        try:
            amount = Decimal(amount.replace(',', '.'))
        except ValueError:
            return None

        if old_unit == new_unit:
            return amount

        if old_unit in self.units and new_unit in self.units[old_unit]:
            result = amount * self.units[old_unit][new_unit]
            return format(result.normalize(), 'f')
        return None

    def post(self, request, *args, **kwargs):
        data = request.POST
        old_unit = data.get('old_unit')
        new_unit = data.get('new_unit')
        amount = data.get('amount')
        possible_units_requested = data.get('possible_units')

        if possible_units_requested:
            possible_units = self.get_possible_units(old_unit)
            return JsonResponse({'status': 'success', 'possible_units': possible_units})

        if old_unit and new_unit and amount:
            result = self.conversion_ingredient(amount, old_unit, new_unit)
            if result is not None:
                return JsonResponse({'status': 'success', 'result': str(result), 'message': 'Ед. измерения обновлены'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Недоступная конвертация'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Недостаточно данных для конвертации'})

