from django.urls import path
from . import views

app_name = "recipes"

urlpatterns = [
    path("", views.RecipeListView.as_view(), name="recipe_list"),
    path("create/", views.RecipeCreateView.as_view(), name="recipe_create"),
    path("<slug:slug>/", views.RecipeDetailView.as_view(), name="recipe_detail"),
    path('like/<int:recipe_id>/', views.toggle_like, name='toggle_like'),
    path('comment/<int:recipe_id>/', views.add_comment, name='add_comment'),
]
