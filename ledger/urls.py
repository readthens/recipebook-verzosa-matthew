from django.urls import path

from . import views

urlpatterns = [
    path('recipes/list', views.recipes_list, name='recipes_list'),
    path('recipe/<int:pk>', views.recipe_detail, name='recipe_detail'),
    path('recipe/add', views.RecipeCreateView.as_view(), name='recipe_add'),
    path('recipe/<int:pk>/add_image', views.RecipeImageCreateView.as_view(), name='recipe_image_add'),
]
