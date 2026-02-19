from django.http import Http404
from django.shortcuts import render

RECIPES = {
    1: {
        "id": 1,
        "name": "Recipe 1",
        "ingredients": [
            {"name": "tomato", "quantity": "3pcs"},
            {"name": "onion", "quantity": "1pc"},
            {"name": "pork", "quantity": "1kg"},
            {"name": "water", "quantity": "1L"},
            {"name": "sinigang mix", "quantity": "1 packet"},
        ],
    },
    2: {
        "id": 2,
        "name": "Recipe 2",
        "ingredients": [
            {"name": "garlic", "quantity": "1 head"},
            {"name": "onion", "quantity": "1pc"},
            {"name": "vinegar", "quantity": "1/2cup"},
            {"name": "water", "quantity": "1 cup"},
            {"name": "salt", "quantity": "1 tablespoon"},
            {"name": "whole black peppers", "quantity": "1 tablespoon"},
            {"name": "pork", "quantity": "1 kilo"},
        ],
    },
}


def recipes_list(request):
    return render(request, "ledger/recipes_list.html", {"recipes": RECIPES.values()})


def recipe_detail(request, recipe_id: int):
    recipe = RECIPES.get(recipe_id)
    if recipe is None:
        raise Http404("Recipe not found")
    return render(request, "ledger/recipe_detail.html", {"recipe": recipe})
