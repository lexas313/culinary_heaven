from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import OuterRef, Exists
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView

from recipes.models import Favorite, Like, Basket, Recipe
from . import forms
from . import models
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, login


# Регистрация пользователя
class RegistrationView(CreateView):
    template_name = 'accounts/registration.html'
    form_class = forms.RegistrationForm
    #  success_url = reverse_lazy('accounts:registration_success')

    # Авторизация пользователя после регистрации
    def form_valid(self, form):
        user = form.save()
        backend = 'django.contrib.auth.backends.ModelBackend'
        login(self.request, user, backend=backend)
        return redirect('home')

# Перенаправление на страницу успешной регистрации
class RegistrationSuccessView(TemplateView):
    template_name = 'accounts/registration_success.html'


# Авторизация пользователя
class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = forms.UserLoginForm
    success_url = reverse_lazy('recipes:all_recipes')


    # def get_success_url(self):  #  Если надо перейти сразу в профиль (передает 'pk')
    #     return reverse_lazy('profile', kwargs={'pk': self.request.user.pk})

    # def get_success_url(self):
    #     return self.success_url


# Перенаправление на страцицу успешной авторизации
class LoginSuccessView(TemplateView):
    template_name = 'accounts/login_success.html'


# Выход (logaut) пользователя
# class UserLogoutView(LogoutView):
#     next_page = reverse_lazy('accounts:login')


# Профиль пользователя
class ProfileView(DetailView):
    model = get_user_model()
    template_name = 'accounts/profile.html'

    # @method_decorator(login_required)  # Закрыть доступ не авторизованным пользователям
    # def dispatch(self, *args, **kwargs):
    #     return super(ProfileView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')  # Получаем username из URL
        return get_object_or_404(get_user_model(), username=username)

    # def get_object(self, queryset=None):  # Получаем текущего пользователя
    #     return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()

        # Если пользователь авторизован, добавляем его данные
        if self.request.user.is_authenticated:
            user = self.request.user
            favorites = Favorite.objects.filter(
                user=user,
                recipe=OuterRef('pk')
            )
            likes = Like.objects.filter(
                user=user,
                recipe=OuterRef('pk')
            )
            baskets = Basket.objects.filter(
                user=user,
                recipe=OuterRef('pk')
            )
            recipes = Recipe.published.for_user(user=user).filter(author=profile_user).select_related('category').annotate(
                is_favorite=Exists(favorites),
                is_liked=Exists(likes),
                is_basket=Exists(baskets)
            )
        else:
            recipes = Recipe.published.filter(author=profile_user).select_related('category')

        # Пагинация
        paginator = Paginator(recipes, 30)
        page = self.request.GET.get('page')
        try:
            paginated_recipes = paginator.page(page)
        except PageNotAnInteger:
            paginated_recipes = paginator.page(1)
        except EmptyPage:
            paginated_recipes = paginator.page(paginator.num_pages)

        context['profile_user'] = profile_user
        context['user'] = self.request.user
        context['recipes'] = recipes
        context['paginated_recipes'] = paginated_recipes  # Добавляем рецепты в контекст

        return context


# Редактирование пользователя
class UpdateUserView(UpdateView):
    template_name = 'accounts/update_user.html'
    form_class = forms.CustomUserChangeForm
    model = models.User

    def get_object(self, queryset=None):  # Получаем текущего пользователя
        return self.request.user

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy('accounts:profile', kwargs={'username': username})

    # def get_success_url(self):  # Если надо перейти сразу в профиль (передает 'pk')
    #     return reverse_lazy('accounts:profile')


class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = forms.UserPasswordChangeForm
    success_url = reverse_lazy('accounts:password_change_done')

    def get_object(self, queryset=None):  # Получаем текущего пользователя
        return self.request.user

    # def get_success_url(self):  # Если надо перейти сразу в профиль передается в reverse_lazy 2-м аргументом kwargs={'pk': self.request.user.pk}
    #     return reverse_lazy('accounts:profile')
