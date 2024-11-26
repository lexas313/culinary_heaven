from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from .models import Recipe, Category, Ingredient, CookingStep, Unit, Tag, CookingMethod


# admin.site.register(Recipe)
# admin.site.register(Category)
# admin.site.register(Ingredient)
# admin.site.register(CookingStep)
# admin.site.register(Unit)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = ('status_moderation', 'moderation_feedback', 'is_published', 'author', 'title', 'slug', 'description', 'category', 'cooking_method', 'tags', 'cooking_time', 'portions', 'image_ready_dish', 'recipe_image')
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('id', 'title', 'description', 'recipe_image', 'date_of_creation', 'is_published', 'status_moderation')
    list_display_links = ('id', 'title', 'description')
    readonly_fields = ('recipe_image', )
    ordering = ('status_moderation', '-date_of_creation')
    list_editable = ('status_moderation', )
    list_per_page = 20
    actions = ('set_moderation_rejected', 'set_moderation_approved', 'set_moderation')
    search_fields = ('id', 'title', 'description')
    list_filter = ('is_published', 'status_moderation')
    filter_horizontal = ('tags', )
    save_on_top = True

    @admin.display(description='Фото блюда')
    def recipe_image(self, recipe: Recipe):
        if recipe.image_ready_dish:
            return mark_safe(f"<img src='{recipe.image_ready_dish.url}' width=150>")
        else:
            return 'Нет фото'

    @admin.action(description='Отклонить модерацию')
    def set_moderation_rejected(self, request, queryset):
        count = queryset.update(status_moderation=Recipe.StatusModeration.REJECTED)
        self.message_user(request, f'Отклонено {count} рецептов', messages.WARNING)

    @admin.action(description='Одобрить модерацию')
    def set_moderation_approved(self, request, queryset):
        count = queryset.update(status_moderation=Recipe.StatusModeration.APPROVED)
        self.message_user(request, f'Одобрено {count} рецептов')

    @admin.action(description='Отправить на модерацию')
    def set_moderation(self, request, queryset):
        count = queryset.update(status_moderation=Recipe.StatusModeration.MODERATION)
        self.message_user(request, f'На модерацию отправлено {count} рецептов', messages.WARNING)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name_category',)}
    list_display = ('id', 'name_category')
    list_display_links = ('id', 'name_category')
    list_per_page = 20


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name_tag',)}
    list_display = ('id', 'name_tag')
    list_display_links = ('id', 'name_tag')
    list_per_page = 20


@admin.register(CookingMethod)
class CookingMethodAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name_cooking_method',)}
    list_display = ('id', 'name_cooking_method')
    list_display_links = ('id', 'name_cooking_method')
    list_per_page = 20


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_unit')
    list_display_links = ('id', 'name_unit')
    list_per_page = 20


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe_ingredient', 'name_ingredient', 'amount', 'unit')
    list_display_links = ('id', 'recipe_ingredient', 'name_ingredient', 'amount', 'unit')
    list_per_page = 20


@admin.register(CookingStep)
class CookingStepAdmin(admin.ModelAdmin):
    fields = ('recipe_cooking_step', 'description_step', 'image_step', 'step_image')
    readonly_fields = ('step_image',)
    list_display = ('id', 'recipe_cooking_step', 'description_step', 'step_image')
    list_display_links = ('id', 'recipe_cooking_step', 'description_step')
    list_per_page = 20

    @admin.display(description='Фото шага')
    def step_image(self, cooking_step: CookingStep):
        if cooking_step.image_step:
            return mark_safe(f"<img src='{cooking_step.image_step.url}' width=150>")
        else:
            return 'Нет фото'