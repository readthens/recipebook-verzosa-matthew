from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic.edit import CreateView

from .forms import RecipeForm, RecipeImageForm
from .models import Profile, Recipe, RecipeImage


def recipes_list(request):
    recipes = Recipe.objects.all()
    return render(request, "ledger/recipes_list.html", {"recipes": recipes})


@login_required
def recipe_detail(request, pk: int):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, "ledger/recipe_detail.html", {"recipe": recipe})


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "ledger/recipe_form.html"

    def form_valid(self, form):
        form.instance.author = get_object_or_404(Profile, user=self.request.user)
        return super().form_valid(form)


class RecipeImageCreateView(LoginRequiredMixin, CreateView):
    model = RecipeImage
    form_class = RecipeImageForm
    template_name = "ledger/recipe_image_form.html"

    def get_recipe(self):
        if not hasattr(self, "_recipe"):
            self._recipe = get_object_or_404(Recipe, pk=self.kwargs["pk"])
        return self._recipe

    def form_valid(self, form):
        form.instance.recipe = self.get_recipe()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe"] = self.get_recipe()
        return context

    def get_success_url(self):
        return reverse("recipe_detail", kwargs={"pk": self.object.recipe.pk})
