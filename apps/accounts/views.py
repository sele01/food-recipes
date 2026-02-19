from django.shortcuts import render, get_list_or_404
from django.contrib.auth import get_user_model
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import CustomUser
from notifications.models import Activity


User = get_user_model()


class ProfileView(DetailView):
    """public profile page for any user
    shows their recipes and basic info"""

    model = User
    template_name = "accounts/profile.html"
    context_object_name = "profile_user"  # the user whose profile is being viewed
    slug_field = "username"  # use username in url
    slug_url_kwarg = "username"  # url: /profile/<username>/

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        # get user's published recipes
        context["recipes"] = user.recipes.filter(is_published=True)
        # get user stat
        context["total_recipes"] = user.recipes.count()
        context["total_likes_received"] = sum(
            recipe.likes.count() for recipe in user.recipes.all()
        )
        # Get user's recent activity (public)
        context["activities"] = (
            Activity.objects.filter(actor=user)
            .exclude(verb="follow")  # Keep follows private
            .select_related("target_content_type")[:20]
        )

        return context


class DashboardView(LoginRequiredMixin, UpdateView):
    """private dashboard for logged in user to edit their profile"""

    model = User
    template_name = "accounts/dashboard.html"
    fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "bio",
        "profile_picture",
        "website",
    ]
    success_url = reverse_lazy("accounts:dashboard")

    def get_object(self):
        return self.request.user  # only allow editing own profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        # get user's published recipes
        context["my_recipes"] = (
            user.recipes.all()
        )  # show all recipes, not just published
        # get user's bookmarked recipes
        context["bookmarks"] = user.bookmark_set.all().select_related(
            "recipe"
        )  # optimize query to get recipe data

        # user recent activity - last 5 recipes created or updated
        context["recent_comments"] = user.comment_set.all()[:5]

        return context
