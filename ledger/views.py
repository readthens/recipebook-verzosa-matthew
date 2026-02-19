from django.shortcuts import get_object_or_404, render

from .models import Recipe


def recipes_list(request):
    recipes = Recipe.objects.all()
    return render(request, "ledger/recipes_list.html", {"recipes": recipes})


def recipe_detail(request, pk: int):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, "ledger/recipe_detail.html", {"recipe": recipe})
