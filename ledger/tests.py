from django.contrib.admin.sites import site
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .admin import RecipeAdmin
from .models import Ingredient, Recipe, RecipeIngredient


class RecipeModelTests(TestCase):
    def test_recipe_str_returns_name(self):
        recipe = Recipe.objects.create(name="Sinigang")
        self.assertEqual(str(recipe), "Sinigang")

    def test_ingredient_str_returns_name(self):
        ingredient = Ingredient.objects.create(name="Tomato")
        self.assertEqual(str(ingredient), "Tomato")

    def test_recipe_get_absolute_url_returns_detail_path(self):
        recipe = Recipe.objects.create(name="Adobo")
        self.assertEqual(recipe.get_absolute_url(), reverse("recipe_detail", kwargs={"pk": recipe.pk}))

    def test_recipeingredient_relations_accessible_via_related_names(self):
        recipe = Recipe.objects.create(name="Sinigang")
        ingredient = Ingredient.objects.create(name="Pork")
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            quantity="1kg",
        )

        self.assertIn(recipe_ingredient, recipe.ingredients.all())
        self.assertIn(recipe_ingredient, ingredient.recipe.all())


class RecipeViewTests(TestCase):
    def setUp(self):
        self.recipe = Recipe.objects.create(name="Sinigang")
        self.ingredient = Ingredient.objects.create(name="Tomato")
        self.recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity="3pcs",
        )

    def test_recipes_list_uses_database_records(self):
        response = self.client.get(reverse("recipes_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sinigang")

    def test_recipe_detail_returns_200_for_existing_pk(self):
        response = self.client.get(reverse("recipe_detail", kwargs={"pk": self.recipe.pk}))
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_returns_404_for_missing_pk(self):
        response = self.client.get(reverse("recipe_detail", kwargs={"pk": 9999}))
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_context_contains_related_ingredients(self):
        response = self.client.get(reverse("recipe_detail", kwargs={"pk": self.recipe.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.recipe_ingredient, response.context["recipe"].ingredients.all())

    def test_rendered_detail_shows_quantity_and_ingredient_name(self):
        response = self.client.get(reverse("recipe_detail", kwargs={"pk": self.recipe.pk}))
        self.assertContains(response, "3pcs Tomato")


class FixtureAndAdminTests(TestCase):
    def test_fixture_loads_without_fk_errors(self):
        call_command("loaddata", "initial_data", verbosity=0)
        self.assertGreaterEqual(Recipe.objects.count(), 2)
        self.assertGreaterEqual(Ingredient.objects.count(), 9)
        self.assertGreaterEqual(RecipeIngredient.objects.count(), 12)

    def test_recipe_registered_in_admin(self):
        admin_class = site._registry.get(Recipe)
        self.assertIsNotNone(admin_class)
        self.assertIsInstance(admin_class, RecipeAdmin)
