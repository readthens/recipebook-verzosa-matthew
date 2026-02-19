from django.urls import path

from . import views

urlpatterns = [
    path('recipes/list', views.recipes_list, name='recipes_list'),
    path('recipe/<int:pk>', views.recipe_detail, name='recipe_detail'),
]
