
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Recipe, Category




class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/recip_list.html'
    context_object_name = 'recipes'
    paginate_by = 9

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_published=True)

        #filter by catgory if selected
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        return context

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'recipe'

    def get_queryset(self):
        return Recipe.objects.filter(is_published=True)
