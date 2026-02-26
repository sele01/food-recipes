from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )

    prep_time = models.IntegerField(help_text="Preparation time in minutes")
    cook_time = models.IntegerField(help_text="Cooking time in minutes")
    servings = models.IntegerField(default=1)

    featured_image = models.ImageField(
        upload_to="recipes/featured/", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            self.slug = slugify(self.title)

            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Recipe.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.value for r in ratings) / len(ratings)
        return 0

    @property
    def rating_count(self):
        return self.ratings.count()


class RecipeImage(models.Model):
    """Multiple images for a recipe"""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="recipes/images/")
    is_featured = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Image for {self.recipe.title}"


class Ingredient(models.Model):
    """Dynamic ingredients for a recipe"""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    name = models.CharField(max_length=200)
    quantity = models.CharField(max_length=100)
    unit = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.name}".strip()


class Step(models.Model):
    """Dynamic cooking steps for a recipe"""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")
    step_number = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to="steps/", blank=True, null=True)

    class Meta:
        ordering = ["step_number"]

    def __str__(self):
        return f"Step {self.step_number}"


class Comment(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.recipe.title}"


# Like model to track user likes on recipes
class Like(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["recipe", "user"]  # one like per user per recipe

    def __str__(self):
        return f"{self.user.username} likes {self.recipe.title}"  # Add user field to Like model


class Bookmark(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="bookmarks"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["recipe", "user"]  # one bookmark per user per recipe

    def __str__(self):
        return f"{self.user.username} bookmarked {self.recipe.title}"


class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)]
    )  # rating value (e.g., 1-5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["recipe", "user"]  # one rating per user per recipe

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title}: {self.value}*"


class Collection(models.Model):
    """a collection of recipes created by a user"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="collections"
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["name", "creator"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} by {self.creator.username}"

    @property
    def recipe_count(self):
        return self.items.count()
class CollectionItem(models.Model):
    """collection of recipes"""

    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name="items"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="collection_items"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ["collection", "recipe"]
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.recipe.title} in {self.collection.name}"
