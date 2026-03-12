from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Ingredient, Profile, Recipe, RecipeImage, RecipeIngredient


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeImageInline(admin.TabularInline):
    model = RecipeImage
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    search_fields = ("name",)
    list_display = ("name", "author", "created_on", "updated_on")
    inlines = [RecipeIngredientInline, RecipeImageInline]


class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    search_fields = ("name",)
    list_display = ("name",)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
