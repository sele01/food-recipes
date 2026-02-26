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
    path("collections/", views.CollectionListView.as_view(), name="collection_list"),
    path(
        "collections/create/",
        views.CollectionCreateView.as_view(),
        name="collection_create",
    ),
    path(
        "collections/<int:pk>/",
        views.CollectionDetailView.as_view(),
        name="collection_detail",
    ),
    path(
        "collections/<int:pk>/edit/",
        views.CollectionUpdateView.as_view(),
        name="collection_edit",
    ),
    path(
        "collections/<int:pk>/delete/",
        views.CollectionDeleteView.as_view(),
        name="collection_delete",
    ),
    path(
        "recipe/<int:recipe_id>/add-to-collection/",
        views.add_to_collection,
        name="add_to_collection",
    ),
    path(
        "collection-item/<int:item_id>/remove/",
        views.remove_from_collection,
        name="remove_from_collection",
    ),
    path("<slug:slug>/", views.RecipeDetailView.as_view(), name="recipe_detail"),
    path("<slug:slug>/edit/", views.RecipeUpdateView.as_view(), name="recipe_edit"),
    path("<slug:slug>/delete/", views.RecipeDeleteView.as_view(), name="recipe_delete"),
]
