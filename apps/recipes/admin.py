from django.contrib import admin
from django.utils.text import slugify
from .models import (
    Category,
    Recipe,
    RecipeImage,
    Ingredient,
    Step,
    Comment,
    Like,
    Bookmark,
    Rating,
    Collection,
    CollectionItem,
)


class RecipeImageInline(admin.TabularInline):
    model = RecipeImage
    extra = 2
    fields = ["image", "is_featured", "caption", "order"]


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 3
    fields = ["name", "quantity", "unit", "order"]


class StepInline(admin.TabularInline):
    model = Step
    extra = 3
    fields = ["step_number", "description", "image"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["title", "creator", "category", "prep_time", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [RecipeImageInline, IngredientInline, StepInline]

    def save_model(self, request, obj, form, change):
        if not obj.creator_id:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


# Register Comment and Like models in admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["recipe", "user", "content_preview", "created_at"]
    list_filter = ["created_at"]

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["recipe", "user", "created_at"]
    list_filter = ["created_at"]


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["recipe", "user", "created_at"]
    list_filter = ["created_at"]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["recipe", "user", "value", "created_at"]
    list_filter = ["created_at"]


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["name", "creator", "recipe_count", "is_public", "created_at"]
    list_filter = ["is_public", "created_at"]
    search_fields = ["name", "description"]


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ["collection", "recipe", "added_at"]
    list_filter = ["added_at"]
