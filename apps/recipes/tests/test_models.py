from django.test import TestCase
from django.contrib.auth import get_user_model
from recipes.models import (
    Recipe,
    Category,
)  # Note: recipes.models, not apps.recipes.models

User = get_user_model()


class RecipeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.category = Category.objects.create(name="Breakfast", slug="breakfast")

    def test_create_recipe(self):
        recipe = Recipe.objects.create(
            title="Test Pancakes",
            description="Yummy",
            creator=self.user,
            category=self.category,
            prep_time=10,
            cook_time=5,
            servings=4,
        )
        self.assertEqual(recipe.title, "Test Pancakes")
