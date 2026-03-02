from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Category

User = get_user_model()


class RecipeViewTests(TestCase):
    """Test recipe views"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.category = Category.objects.create(name="Breakfast", slug="breakfast")

        self.recipe = Recipe.objects.create(
            title="Pancakes",
            description="Yummy pancakes",
            creator=self.user,
            category=self.category,
            prep_time=10,
            cook_time=5,
            servings=4,
            slug="pancakes",
        )

    def test_recipe_list_view(self):
        url = reverse("recipes:recipe_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipe_list.html")
        self.assertContains(response, "Pancakes")

    def test_recipe_detail_view(self):
        url = reverse("recipes:recipe_detail", kwargs={"slug": "pancakes"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipe_detail.html")
        self.assertContains(response, "Yummy pancakes")

    def test_recipe_detail_404_for_nonexistent(self):
        url = reverse("recipes:recipe_detail", kwargs={"slug": "nonexistent"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
