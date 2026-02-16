from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Recipe, Ingredient, Step, RecipeImage, Category

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RecipeForm, IngredientForm, StepForm
from django.forms import inlineformset_factory


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Like, Comment
from django.contrib import messages


class RecipeListView(ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    paginate_by = 9

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_published=True)

        # filter by category if selected
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()

        return context


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"

    def get_queryset(self):
        return Recipe.objects.filter(is_published=True)


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    fields = [
        "title",
        "description",
        "category",
        "prep_time",
        "cook_time",
        "servings",
        "featured_image",
    ]
    template_name = "recipes/recipe_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create formsets
        IngredientFormSet = inlineformset_factory(
            Recipe,
            Ingredient,
            fields=["name", "quantity", "unit"],
            extra=3,
            can_delete=True,
        )

        StepFormSet = inlineformset_factory(
            Recipe,
            Step,
            fields=["step_number", "description"],
            extra=3,
            can_delete=True,
        )

        if self.request.POST:
            context["ingredient_formset"] = IngredientFormSet(
                self.request.POST, instance=self.object
            )
            context["step_formset"] = StepFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["ingredient_formset"] = IngredientFormSet(instance=self.object)
            context["step_formset"] = StepFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        form.instance.creator = self.request.user
        context = self.get_context_data()
        ingredient_formset = context["ingredient_formset"]
        step_formset = context["step_formset"]

        if ingredient_formset.is_valid() and step_formset.is_valid():
            self.object = form.save()
            ingredient_formset.instance = self.object
            step_formset.instance = self.object
            ingredient_formset.save()
            step_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("recipes:recipe_list")


@login_required
def toggle_like(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    like = Like.objects.filter(recipe=recipe, user=request.user)

    if like.exists():
        like.delete()
    else:
        Like.objects.create(recipe=recipe, user=request.user)

    return redirect("recipes:recipe_detail", slug=recipe.slug)


@login_required
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    content = request.POST.get("content")

    if content:
        Comment.objects.create(recipe=recipe, user=request.user, content=content)
    else:
        messages.error(request, "Comment cannot be empty.")

    return redirect("recipes:recipe_detail", slug=recipe.slug)
