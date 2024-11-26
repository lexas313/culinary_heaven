from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.decorators.cache import cache_page
from culinary_heaven.settings import base


app_name = 'recipes'

urlpatterns = [
    path('detail_recipe/<slug:slug>/', views.DetailRecipeView.as_view(), name='detail_recipe'),
    path('add_recipe/', views.AddRecipeView.as_view(), name='add_recipe'),
    path('update_recipe/<slug:slug>/', views.UpdateRecipeView.as_view(), name='update_recipe'),
    path('category/<slug:slug>/', views.RecipeCategory.as_view(), name='category'),
    path('tag/', views.RecipeTag.as_view(), name='tag'),
    path('favorite/', views.RecipeFavorite.as_view(), name='favorite'),
    path('add_to_favorites/', views.AddToFavoritesView.as_view(), name='add_to_favorites'),
    # path('like_recipe/', views.LikeView.as_view(), name='like_recipe'),
    path('delete_recipe/<int:pk>/', views.DeleteRecipeView.as_view(), name='delete_recipe'),
    path('comment_create_view/<int:pk>/comments/create/', views.CommentCreateView.as_view(), name='comment_create_view'),
    path('comment/<int:comment_id>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('basket/', views.BasketView.as_view(), name='basket'),
    path('add_basket/', views.AddBasketView.as_view(), name='add_basket'),
    path('increase_quantity/', views.IncreaseQuantityView.as_view(), name='increase_quantity'),
    path('decrease_quantity/', views.DecreaseQuantityView.as_view(), name='decrease_quantity'),
    path('delete_basket_item/', views.DeleteBasketItemView.as_view(), name='delete_basket_item'),
    path('delete_basket/', views.DeleteBasketView.as_view(), name='delete_basket'),
    path('delete_ingredient/', views.DeleteIngredientView.as_view(), name='delete_ingredient'),
    path('update_basket_ingredient/', views.UpdateBasketIngredient.as_view(), name='update_basket_ingredient'),
    path('convert_unit/', views.ConvertUnitView.as_view(), name='convert_unit'),
]

if base.DEBUG:
    urlpatterns += [
        path('all_recipes/', views.AllRecipeView.as_view(), name='all_recipes'),
    ]
else:
    urlpatterns += [
        path('all_recipes/', cache_page(60 * 60)(views.AllRecipeView.as_view()), name='all_recipes'),
    ]
