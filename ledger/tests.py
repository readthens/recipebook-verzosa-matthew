import tempfile

from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .admin import RecipeAdmin, RecipeImageInline
from .models import Ingredient, Profile, Recipe, RecipeImage, RecipeIngredient


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


def make_test_image_file(name: str = "recipe.gif") -> SimpleUploadedFile:
    return SimpleUploadedFile(
        name,
        (
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
            b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00"
            b"\x00\x02\x02D\x01\x00;"
        ),
        content_type="image/gif",
    )


class MediaTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._temp_media_dir = tempfile.TemporaryDirectory()
        cls._media_override = override_settings(MEDIA_ROOT=cls._temp_media_dir.name)
        cls._media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._media_override.disable()
        cls._temp_media_dir.cleanup()
        super().tearDownClass()


class RecipeModelTests(MediaTestCase):
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

    def test_recipeimage_relations_accessible_via_related_name(self):
        recipe = Recipe.objects.create(name="Kare-Kare", author=self.profile)
        recipe_image = RecipeImage.objects.create(
            recipe=recipe,
            image=make_test_image_file("kare-kare.gif"),
            description="Freshly plated kare-kare",
        )

        self.assertIn(recipe_image, recipe.images.all())

    def test_recipeimage_requires_image(self):
        recipe = Recipe.objects.create(name="Tinola", author=self.profile)
        recipe_image = RecipeImage(recipe=recipe, description="No image attached")

        with self.assertRaises(ValidationError):
            recipe_image.full_clean()

    def test_recipeimage_description_max_length_enforced(self):
        recipe = Recipe.objects.create(name="Afritada", author=self.profile)
        recipe_image = RecipeImage(
            recipe=recipe,
            image=make_test_image_file("afritada.gif"),
            description="A" * 256,
        )

        with self.assertRaises(ValidationError):
            recipe_image.full_clean()


class RecipeViewTests(MediaTestCase):
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

    def test_recipes_list_hides_add_recipe_link_when_logged_out(self):
        response = self.client.get(reverse("recipes_list"))
        self.assertNotContains(response, reverse("recipe_add"))

    def test_recipes_list_shows_add_recipe_link_when_logged_in(self):
        self.client.login(username=self.user.username, password="strong-pass-123")
        response = self.client.get(reverse("recipes_list"))
        self.assertContains(response, reverse("recipe_add"))

    def test_recipe_detail_redirects_to_login_when_unauthenticated(self):
        detail_url = reverse("recipe_detail", kwargs={"pk": self.recipe.pk})
        response = self.client.get(detail_url)
        self.assertRedirects(response, f"{reverse('login')}?next={detail_url}")

    def test_recipe_add_redirects_to_login_when_unauthenticated(self):
        add_url = reverse("recipe_add")
        response = self.client.get(add_url)
        self.assertRedirects(response, f"{reverse('login')}?next={add_url}")

    def test_recipe_image_add_redirects_to_login_when_unauthenticated(self):
        add_image_url = reverse("recipe_image_add", kwargs={"pk": self.recipe.pk})
        response = self.client.get(add_image_url)
        self.assertRedirects(response, f"{reverse('login')}?next={add_image_url}")

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

    def test_rendered_detail_shows_add_image_link_when_authenticated(self):
        self.client.login(username=self.user.username, password="strong-pass-123")
        response = self.client.get(reverse("recipe_detail", kwargs={"pk": self.recipe.pk}))
        self.assertContains(response, reverse("recipe_image_add", kwargs={"pk": self.recipe.pk}))

    def test_rendered_detail_shows_uploaded_recipe_images(self):
        RecipeImage.objects.create(
            recipe=self.recipe,
            image=make_test_image_file("sinigang.gif"),
            description="Fresh bowl",
        )

        self.client.login(username=self.user.username, password="strong-pass-123")
        response = self.client.get(reverse("recipe_detail", kwargs={"pk": self.recipe.pk}))

        recipe_image = self.recipe.images.get()
        self.assertContains(response, recipe_image.image.url)
        self.assertContains(response, 'alt="Fresh bowl"', html=False)

    def test_recipe_add_creates_recipe_for_logged_in_users_profile(self):
        self.client.login(username=self.user.username, password="strong-pass-123")
        response = self.client.post(reverse("recipe_add"), {"name": "Caldereta"})

        new_recipe = Recipe.objects.get(name="Caldereta")
        self.assertRedirects(response, reverse("recipe_detail", kwargs={"pk": new_recipe.pk}))
        self.assertEqual(new_recipe.author, self.profile)

    def test_recipe_image_add_creates_image_and_redirects_to_detail(self):
        self.client.login(username=self.user.username, password="strong-pass-123")
        response = self.client.post(
            reverse("recipe_image_add", kwargs={"pk": self.recipe.pk}),
            {
                "image": make_test_image_file("uploaded.gif"),
                "description": "Serving suggestion",
            },
        )

        self.assertEqual(RecipeImage.objects.filter(recipe=self.recipe).count(), 1)
        self.assertRedirects(response, reverse("recipe_detail", kwargs={"pk": self.recipe.pk}))

    def test_recipe_image_add_without_image_is_invalid(self):
        self.client.login(username=self.user.username, password="strong-pass-123")
        response = self.client.post(
            reverse("recipe_image_add", kwargs={"pk": self.recipe.pk}),
            {"description": "Missing file"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecipeImage.objects.filter(recipe=self.recipe).count(), 0)
        self.assertFormError(response.context["form"], "image", "This field is required.")


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

    def test_recipe_admin_includes_recipeimage_inline(self):
        admin_class = site._registry.get(Recipe)
        self.assertIn(RecipeImageInline, admin_class.inlines)
