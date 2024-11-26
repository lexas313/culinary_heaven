from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordChangeForm, \
    PasswordResetForm, SetPasswordForm
from captcha.fields import CaptchaField


class RegistrationForm(UserCreationForm):  # Регистрация
    username = forms.CharField(label='Логин')
    email = forms.CharField(label='E-mail')
    #first_name = forms.CharField(label='Имя', required=False)
    #last_name = forms.CharField(label='Фамилия', required=False)
    #gender = forms.ChoiceField(label='Пол', choices=[('', '-Не выбран-')] + get_user_model().GENDER_CHOICES, required=False)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)
    privacy_policy = forms.BooleanField(label='Я согласен с политикой конфиденциальности', initial=True, required=True)
    captcha = CaptchaField(label='Введите текст с картинки')


    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.set_password(self.cleaned_data["password1"])
    #     if commit:
    #         user.save()
    #         if hasattr(self, "save_m2m"):
    #             self.save_m2m()
    #     return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ['privacy_policy']:
                field.widget.attrs['class'] = 'form-fields'

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким e-mail уже зарегистрирован")
        else:
            return email


class UserLoginForm(AuthenticationForm):  # Авторизация
    username = forms.CharField(label='Логин/E-mail', widget=forms.TextInput)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-fields'


class CustomUserChangeForm(UserChangeForm):  # Редактирование профиля
    class Meta:
        model = get_user_model()
        fields = ['image_profile', 'username', 'first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'image_profile': forms.ClearableFileInput(attrs={'class': 'custom-file-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']
        for name, field in self.fields.items():
            if name not in ['image_profile']:
                field.widget.attrs['class'] = 'form-fields'


class UserPasswordChangeForm(PasswordChangeForm):  # Смена пароля
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Mete:
        model = get_user_model()
        fields = ['password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-fields'


class UserPasswordResetForm(PasswordResetForm):  # Форма для email на который придет письмо для смены пароля
    class Meta:
        model = get_user_model()
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-fields'


class UserSetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-fields'
