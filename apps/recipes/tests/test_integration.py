from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Category

User = get_user_model()


class RecipeCreationIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.category = Category.objects.create(name="Breakfast", slug="breakfast")

    def test_create_recipe_with_ingredients_and_steps(self):
        self.client.login(username="testuser", password="testpass123")

        recipe_data = {
            "title": "Integration Test Pancakes",
            "description": "Testing full flow",
            "category": self.category.id,
            "prep_time": 10,
            "cook_time": 5,
            "servings": 4,
            "ingredients-TOTAL_FORMS": "2",
            "ingredients-INITIAL_FORMS": "0",
            "ingredients-0-name": "Flour",
            "ingredients-0-quantity": "2",
            "ingredients-0-unit": "cups",
            "ingredients-1-name": "Milk",
            "ingredients-1-quantity": "1.5",
            "ingredients-1-unit": "cups",
            "steps-TOTAL_FORMS": "2",
            "steps-INITIAL_FORMS": "0",
            "steps-0-step_number": "1",
            "steps-0-description": "Mix dry ingredients",
            "steps-1-step_number": "2",
            "steps-1-description": "Add wet ingredients",
        }

        response = self.client.post(reverse("recipes:recipe_create"), recipe_data)
        self.assertEqual(response.status_code, 302)

        recipe = Recipe.objects.get(title="Integration Test Pancakes")
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertEqual(recipe.steps.count(), 2)
