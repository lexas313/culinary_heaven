import django_filters
from django import forms
from django.db.models import Count, Q
from django.db.models.functions import Lower
from django_filters import CharFilter, ModelMultipleChoiceFilter

from .models import Recipe, Category, Unit, Ingredient, CookingStep, Tag, Comment, CookingMethod
from django.forms import modelformset_factory, CheckboxSelectMultiple
from django_select2.forms import Select2MultipleWidget


class RecipeForm(forms.ModelForm):
    title = forms.CharField(label='Название блюда')
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label='Категория')
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Описание блюда')
    portions = forms.IntegerField(label='Количество порций')
    cooking_time = forms.IntegerField(label='Время приготовления')
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        label='Теги',
        widget=Select2MultipleWidget(attrs={'class': 'select2-multiple'}),
        required=False
    )
    cooking_method = forms.ModelMultipleChoiceField(
        queryset=CookingMethod.objects.all(),
        label='Способ приготовления',
        widget=Select2MultipleWidget(attrs={'class': 'select2-multiple'}),
        required=False
    )

    class Meta:
        model = Recipe
        fields = (
        'title', 'description', 'category', 'cooking_method', 'tags', 'is_published', 'portions', 'cooking_time', 'image_ready_dish')
        widgets = {
            'image_ready_dish': forms.ClearableFileInput(attrs={'class': 'custom-file-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = '-Выберите категорию-'
        for name, field in self.fields.items():
            if name not in ['image_ready_dish', 'tags', 'cooking_method']:
                field.widget.attrs['class'] = 'form-fields'


class IngredientsForm(forms.ModelForm):
    name_ingredient = forms.CharField(label='Название ингредиента')
    amount = forms.DecimalField(label='Кол-во', max_digits=10, decimal_places=2)
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), label='Мера')

    class Meta:
        model = Recipe
        fields = ('name_ingredient', 'amount', 'unit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].empty_label = '-----'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-fields'


class CookingStepForm(forms.ModelForm):
    class Meta:
        model = CookingStep
        fields = ('description_step', 'image_step')
        widgets = {
            'description_step': forms.Textarea(attrs={'rows': 4}),
            'image_step': forms.ClearableFileInput(attrs={'class': 'custom-file-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description_step'].widget.attrs['class'] = 'form-fields'
        # for field in self.fields:
        #     self.fields[field].widget.attrs['class'] = 'form-fields'


class CommentCreateForm(forms.ModelForm):
    """
    Форма добавления комментариев к статьям
    """
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='',
                              widget=forms.Textarea(attrs={'cols': 30, 'rows': 5, 'placeholder': 'Комментарий'}))
    name = forms.CharField(label='Имя', max_length=255,
                           widget=forms.TextInput(attrs={'placeholder': 'Введите ваше имя'}), required=False)
    email = forms.EmailField(label='Email', max_length=255,
                             widget=forms.TextInput(attrs={'placeholder': 'Введите ваш email'}), required=False)

    class Meta:
        model = Comment
        fields = ('content', 'name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-fields'

