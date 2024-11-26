from captcha.views import captcha_refresh
from django.contrib import admin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, LogoutView, PasswordChangeDoneView
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from . import views
from . import forms

app_name = 'accounts'

urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),

    path('registration_success/', views.RegistrationSuccessView.as_view(), name='registration_success'),
    path('login_success/', views.LoginSuccessView.as_view(), name='login_success'),

    path('password_change/', views.UserPasswordChangeView.as_view(), name='password_change'),

    path('password_change/done/', PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'),
        name='password_change_done'),

    path('update_user/', views.UpdateUserView.as_view(), name='update_user'),

    path('password-reset/', PasswordResetView.as_view(
        template_name="accounts/password_reset_form.html",
        form_class=forms.UserPasswordResetForm,
        email_template_name='accounts/password_reset_email.html',
        success_url=reverse_lazy('accounts:password_reset_done')
    ),
        name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html"),
        name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        form_class=forms.UserSetPasswordForm,
        success_url=reverse_lazy('accounts:password_reset_complete')
    ),
        name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html"),
        name='password_reset_complete'),

    path('privacy_policy/', TemplateView.as_view(template_name='accounts/privacy_policy.html'), name='privacy_policy'),
    path('captcha/refresh/', captcha_refresh, name='captcha-refresh'),
]
