from django.urls import path
from . import views

app_name = "recipes"

urlpatterns = [
    path("", views.RecipeListView.as_view(), name="recipe_list"),
    path("feed/", views.FollowingFeedView.as_view(), name="following_feed"),
    path("create/", views.RecipeCreateView.as_view(), name="recipe_create"),
    path("like/<int:recipe_id>/", views.toggle_like, name="toggle_like"),
    path("comment/<int:recipe_id>/", views.add_comment, name="add_comment"),
    path("bookmark/<int:recipe_id>/", views.toggle_bookmark, name="toggle_bookmark"),
    path("rate/<int:recipe_id>/", views.rate_recipe, name="rate_recipe"),
    path("bookmarks/", views.BookmarkListView.as_view(), name="bookmarks"),
    path("<slug:slug>/", views.RecipeDetailView.as_view(), name="recipe_detail"),
    path("<slug:slug>/edit/", views.RecipeUpdateView.as_view(), name="recipe_edit"),
    path("<slug:slug>/delete/", views.RecipeDeleteView.as_view(), name="recipe_delete"),
]
