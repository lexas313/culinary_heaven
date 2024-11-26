"""
URL configuration for culinary_heaven project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from recipes.views import AllRecipeView
from .settings import base
from django.views.decorators.cache import cache_page


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('recipes/', include('recipes.urls', namespace='recipes')),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
    path("select2/", include("django_select2.urls")),
    path('captcha/', include('captcha.urls')),
]

if base.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
        path('', AllRecipeView.as_view(), name='home'),
    ] + static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)
else:
    urlpatterns += [
        path('', cache_page(60 * 60)(AllRecipeView.as_view()), name='home'),
    ]

admin.site.site_header = 'Панель администрирования'
admin.site.index_title = 'Кулинарный сайт'
