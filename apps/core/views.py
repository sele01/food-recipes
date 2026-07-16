from django.views.generic import TemplateView
from apps.recipes.models import Recipe, Category
from django.contrib.auth import get_user_model

User = get_user_model()

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics
        try:
            context['recipe_count'] = Recipe.objects.filter(is_published=True).count()
        except Exception:
            context['recipe_count'] = 0

        try:
            context['category_count'] = Category.objects.count()
        except Exception:
            context['category_count'] = 0

        try:
            context['featured_recipes'] = Recipe.objects.filter(is_published=True).order_by('-created_at')[:6]
        except Exception:
            context['featured_recipes'] = []

        try:
            context['categories'] = Category.objects.all()
        except Exception:
            context['categories'] = []
        try:
            context['user_count'] = User.objects.count()
        except Exception:
            context['user_count'] = 0
        # Featured recipes (latest 6)
        context['featured_recipes'] = Recipe.objects.filter(is_published=True).order_by('-created_at')[:6]

        # Categories
        context['categories'] = Category.objects.all()

        return context