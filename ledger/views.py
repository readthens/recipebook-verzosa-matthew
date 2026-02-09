from django.shortcuts import render

RECIPE_1 = {
    "name": "Recipe 1",
    "ingredients": [
        {"name": "tomato", "quantity": "3pcs"},
        {"name": "onion", "quantity": "1pc"},
        {"name": "pork", "quantity": "1kg"},
        {"name": "water", "quantity": "1L"},
        {"name": "sinigang mix", "quantity": "1 packet"},
    ],
    "link": "/recipe/1",
}

RECIPE_2 = {
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
    "link": "/recipe/2",
}


def recipes_list(request):
    return render(request, "ledger/recipes_list.html", {"recipes": [RECIPE_1, RECIPE_2]})


def recipe_1(request):
    return render(request, "ledger/recipe_1.html", {"recipe": RECIPE_1})


def recipe_2(request):
    return render(request, "ledger/recipe_2.html", {"recipe": RECIPE_2})
