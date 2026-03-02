from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .admin import RecipeAdmin
from .models import Ingredient, Profile, Recipe, RecipeIngredient


def create_profile(username: str = "author") -> Profile:
    user = User.objects.create_user(
        username=username,
        password="strong-pass-123",
        email=f"{username}@example.com",
    )
    return Profile.objects.create(
        user=user,
        name=username.title(),
        short_bio="A" * 256,
    )


class RecipeModelTests(TestCase):
    def setUp(self):
        self.profile = create_profile()

    def test_recipe_str_returns_name(self):
        recipe = Recipe.objects.create(name="Sinigang", author=self.profile)
        self.assertEqual(str(recipe), "Sinigang")

    def test_ingredient_str_returns_name(self):
        ingredient = Ingredient.objects.create(name="Tomato")
        self.assertEqual(str(ingredient), "Tomato")

    def test_recipe_get_absolute_url_returns_detail_path(self):
        recipe = Recipe.objects.create(name="Adobo", author=self.profile)
        self.assertEqual(recipe.get_absolute_url(), reverse("recipe_detail", kwargs={"pk": recipe.pk}))

    def test_recipeingredient_relations_accessible_via_related_names(self):
        recipe = Recipe.objects.create(name="Sinigang", author=self.profile)
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
        self.profile = create_profile("viewer")
        self.user = self.profile.user
        self.recipe = Recipe.objects.create(name="Sinigang", author=self.profile)
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

    def test_recipe_detail_redirects_to_login_when_unauthenticated(self):
        detail_url = reverse("recipe_detail", kwargs={"pk": self.recipe.pk})
        response = self.client.get(detail_url)
        self.assertRedirects(response, f"{reverse('login')}?next={detail_url}")

    def test_recipe_detail_returns_200_for_existing_pk_when_authenticated(self):
        self.client.login(username=self.user.username, password="strong-pass-123")
        response = self.client.get(reverse("recipe_detail", kwargs={"pk": self.recipe.pk}))
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_returns_404_for_missing_pk_when_authenticated(self):
        self.client.login(username=self.user.username, password="strong-pass-123")
        response = self.client.get(reverse("recipe_detail", kwargs={"pk": 9999}))
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_context_contains_related_ingredients_when_authenticated(self):
        self.client.login(username=self.user.username, password="strong-pass-123")
        response = self.client.get(reverse("recipe_detail", kwargs={"pk": self.recipe.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.recipe_ingredient, response.context["recipe"].ingredients.all())

    def test_rendered_detail_shows_quantity_ingredient_and_author_when_authenticated(self):
        self.client.login(username=self.user.username, password="strong-pass-123")
        response = self.client.get(reverse("recipe_detail", kwargs={"pk": self.recipe.pk}))
        self.assertContains(response, "3pcs Tomato")
        self.assertContains(response, self.profile.name)


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
