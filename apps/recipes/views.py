from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import (
    Recipe,
    Ingredient,
    Step,
    RecipeImage,
    Category,
    Like,
    Comment,
    Bookmark,
    Rating,
    Collection,
    CollectionItem,
)

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import RecipeForm, IngredientForm, StepForm
from django.forms import inlineformset_factory


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Like, Comment
from django.contrib import messages

from django.db.models import Q


from django.contrib.contenttypes.models import ContentType
from notifications.models import Activity


from django.views.generic.edit import UpdateView, DeleteView


class RecipeListView(ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    paginate_by = 9

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_published=True)

        # filter by category if selected
        # search by title
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
            )
        # filter by category if selected
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # filter by prep time(max minutes)
        max_time = self.request.GET.get("max_time")
        if max_time:
            queryset = queryset.filter(prep_time__lte=max_time)

        # filter by ingredient
        ingredient = self.request.GET.get("ingredient")
        if ingredient:
            queryset = queryset.filter(
                ingredients__name__icontains=ingredient
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()

        # pass search parameters to template for pagination links
        context["search_query"] = self.request.GET.get("search", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["max_time"] = self.request.GET.get("max_time", "")
        context["ingredient"] = self.request.GET.get("ingredient", "")

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
            Activity.objects.create(
                actor=self.request.user,
                verb="create",
                target=self.object,
                recipient=None,  # Public creation, no specific recipient
            )
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
        comment = Comment.objects.create(
            recipe=recipe, user=request.user, content=content
        )
        # CREATE ACTIVITY
        Activity.objects.create(
            actor=request.user,
            verb="comment",
            target=comment,  # Point to the comment itself
            recipient=recipe.creator,  # Notify recipe owner
        )
    else:
        messages.error(request, "Comment cannot be empty.")

    return redirect("recipes:recipe_detail", slug=recipe.slug)


@login_required
def toggle_bookmark(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    bookmark = Bookmark.objects.filter(recipe=recipe, user=request.user)

    if bookmark.exists():
        bookmark.delete()
    else:
        Bookmark.objects.create(recipe=recipe, user=request.user)

    return redirect("recipes:recipe_detail", slug=recipe.slug)


# Rating view to handle user ratings on recipes
@login_required
def rate_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    value = request.POST.get("value")

    if value:
        rating, created = Rating.objects.get_or_create(
            recipe=recipe, user=request.user, defaults={"value": value}
        )

    return redirect("recipes:recipe_detail", slug=recipe.slug)


class BookmarkListView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = "recipes/bookmarks.html"
    context_object_name = "bookmarks"

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related("recipe")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipes"] = [bookmark.recipe for bookmark in context["bookmarks"]]
        return context


@login_required
def toggle_like(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    like = Like.objects.filter(recipe=recipe, user=request.user)
    if like.exists():
        like.delete()

        Activity.objects.filter(
            target_content_type=ContentType.objects.get_for_model(recipe),
            target_object_id=recipe.id,
            actor=request.user,
            verb="like",
        ).delete()
    else:
        Like.objects.create(recipe=recipe, user=request.user)

        Activity.objects.create(
            actor=request.user, verb="like", target=recipe, recipient=recipe.creator
        )

    return redirect("recipes:recipe_detail", slug=recipe.slug)


class RecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View to handle updating a recipe. Only the creator can update."""

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

    def test_func(self):
        """check if the logged in user is the creator of the recipe"""
        recipe = self.get_object()
        return self.request.user == recipe.creator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.get_object()

        IngredientFormSet = inlineformset_factory(
            Recipe,
            Ingredient,
            fields=["name", "quantity", "unit"],
            extra=1,
            can_delete=True,
        )
        StepFormSet = inlineformset_factory(
            Recipe,
            Step,
            fields=["step_number", "description"],
            extra=1,
            can_delete=True,
        )

        if self.request.POST:
            context["ingredient_formset"] = IngredientFormSet(
                self.request.POST, instance=recipe
            )
            context["step_formset"] = StepFormSet(self.request.POST, instance=recipe)
        else:
            context["ingredient_formset"] = IngredientFormSet(instance=recipe)
            context["step_formset"] = StepFormSet(instance=recipe)

        return context

    def form_valid(self, form):
        print("=== FORM VALID CALLED ===")
        context = self.get_context_data()
        ingredient_formset = context["ingredient_formset"]
        step_formset = context["step_formset"]

        print(f"Ingredient formset valid: {ingredient_formset.is_valid()}")
        print(f"Step formset valid: {step_formset.is_valid()}")

        if ingredient_formset.is_valid() and step_formset.is_valid():
            self.object = form.save()
            print(f"Recipe saved with ID: {self.object.id}")

            ingredient_formset.instance = self.object
            step_formset.instance = self.object
            ingredient_formset.save()
            step_formset.save()
            print("Ingredients and steps saved")

            return super().form_valid(form)
        else:
            print("Formset errors:")
            print(ingredient_formset.errors)
            print(step_formset.errors)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("recipes:recipe_detail", kwargs={"slug": self.object.slug})


class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View to handle deleting a recipe. Only the creator can delete."""

    model = Recipe
    template_name = "recipes/recipe_confirm_delete.html"
    success_url = reverse_lazy("recipes:recipe_list")

    def test_func(self):
        """check if the logged in user is the creator of the recipe"""
        recipe = self.get_object()
        return self.request.user == recipe.creator

    def delete(self, request, *args, **kwargs):
        """Override delete to also remove related activities"""
        self.object = self.get_object()
        recipe_id = self.object.id

        # Delete related activities
        Activity.objects.filter(
            target_content_type=ContentType.objects.get_for_model(self.object),
            target_object_id=recipe_id,
        ).delete()

        messages.success(
            request, "Recipe and all related activities have been deleted successfully."
        )
        return super().delete(request, *args, **kwargs)


class FollowingFeedView(LoginRequiredMixin, ListView):
    """Show recipes from users that the logged-in user is following"""

    model = Recipe
    template_name = "recipes/following_feed.html"
    context_object_name = "recipes"
    paginate_by = 9

    def get_queryset(self):
        following_users = self.request.user.following.all().values_list(
            "followed", flat=True
        )

        return Recipe.objects.filter(
            creator_id__in=following_users, is_published=True
        ).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["feed_type"] = "following"
        return context


class CollectionListView(ListView):
    """View to list all collections, with option to filter by user"""

    model = Collection
    template_name = "recipes/collection_list.html"
    context_object_name = "collections"
    paginate_by = 12

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.GET.get("mine"):
            return Collection.objects.filter(creator=self.request.user)
        return Collection.objects.filter(is_public=True)


class CollectionDetailView(DetailView):
    """View to show details of a collection, including its recipes"""

    model = Collection
    template_name = "recipes/collection_detail.html"
    context_object_name = "collection"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection = self.get_object()

        if self.request.user.is_authenticated:
            user_collection = Collection.objects.filter(
                creator=self.request.user
            ).exclude(id=collection.id)
            context["user_collections"] = user_collection

        return context


class CollectionCreateView(LoginRequiredMixin, CreateView):
    """create a new collection"""

    model = Collection
    fields = ["name", "description", "is_public"]
    template_name = "recipes/collection_form.html"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("recipes:collection_detail", kwargs={"pk": self.object.pk})


class CollectionCreateView(LoginRequiredMixin, CreateView):
    """create a new collection"""

    model = Collection
    fields = ["name", "description", "is_public"]
    template_name = "recipes/collection_form.html"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("recipes:collection_detail", kwargs={"pk": self.object.pk})


class CollectionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """edit a collection"""

    model = Collection
    fields = ["name", "description", "is_public"]
    template_name = "recipes/collection_form.html"

    def test_func(self):
        collection = self.get_object()
        return self.request.user == collection.creator

    def get_success_url(self):
        return reverse_lazy("recipes:collection_detail", kwargs={"pk": self.object.pk})


class CollectionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """delete a collection"""

    model = Collection
    template_name = "recipes/collection_confirm_delete.html"
    success_url = reverse_lazy("recipes:collection_list")

    def test_func(self):
        collection = self.get_object()
        return self.request.user == collection.creator


@login_required
def add_to_collection(request, recipe_id):
    """Add a recipe to a collection"""

    recipe = get_object_or_404(Recipe, id=recipe_id)
    collection_id = request.POST.get("collection_id")

    if collection_id:
        collection = get_object_or_404(
            Collection, id=collection_id, creator=request.user
        )
        item, created = CollectionItem.objects.get_or_create(
            collection=collection, recipe=recipe
        )

        if created:
            messages.success(request, f'Added to collection "{collection.name}".')
        else:
            messages.info(request, f'"{collection.name}" already contains this recipe.')
    else:
        messages.error(request, "No collection selected.")

    return redirect("recipes:recipe_detail", slug=recipe.slug)


@login_required
def remove_from_collection(request, item_id):
    """Remove a recipe from a collection"""

    item = get_object_or_404(
        CollectionItem, id=item_id, collection__creator=request.user
    )
    collection = item.collection
    item.delete()
    messages.success(request, f'Removed from collection "{collection.name}".')

    return redirect("recipes:collection_detail", pk=collection.pk)
