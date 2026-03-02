from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Category, Like, Comment, Bookmark, Rating

User = get_user_model()


class UserRecipeWorkflowTests(TestCase):
    """Test complete user workflows"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Breakfast", slug="breakfast")

    def test_complete_recipe_lifecycle(self):
        """Test: Create → View → Edit → Delete a recipe"""

        # 1. Login
        self.client.login(username="testuser", password="testpass123")

        # 2. Create recipe
        create_url = reverse("recipes:recipe_create")
        recipe_data = {
            "title": "Integration Recipe",
            "description": "Testing full flow",
            "category": self.category.id,
            "prep_time": 10,
            "cook_time": 5,
            "servings": 4,
            "ingredients-TOTAL_FORMS": "1",
            "ingredients-INITIAL_FORMS": "0",
            "ingredients-0-name": "Flour",
            "ingredients-0-quantity": "2",
            "ingredients-0-unit": "cups",
            "steps-TOTAL_FORMS": "1",
            "steps-INITIAL_FORMS": "0",
            "steps-0-step_number": "1",
            "steps-0-description": "Mix ingredients",
        }

        create_response = self.client.post(create_url, recipe_data)
        self.assertEqual(create_response.status_code, 302)

        # Get the created recipe
        recipe = Recipe.objects.get(title="Integration Recipe")
        self.assertIsNotNone(recipe.slug)

        # 3. View recipe
        detail_url = reverse("recipes:recipe_detail", kwargs={"slug": recipe.slug})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Integration Recipe")
        self.assertContains(detail_response, "Flour")
        self.assertContains(detail_response, "Mix ingredients")

        # 4. Edit recipe
        edit_url = reverse("recipes:recipe_edit", kwargs={"slug": recipe.slug})
        edit_data = {
            "title": "Updated Recipe",
            "description": "Updated description",
            "category": self.category.id,
            "prep_time": 15,
            "cook_time": 10,
            "servings": 6,
            "ingredients-TOTAL_FORMS": "2",
            "ingredients-INITIAL_FORMS": "1",
            "ingredients-0-id": recipe.ingredients.first().id,
            "ingredients-0-name": "Flour",
            "ingredients-0-quantity": "3",
            "ingredients-0-unit": "cups",
            "ingredients-1-name": "Sugar",
            "ingredients-1-quantity": "1",
            "ingredients-1-unit": "cup",
            "steps-TOTAL_FORMS": "1",
            "steps-INITIAL_FORMS": "1",
            "steps-0-id": recipe.steps.first().id,
            "steps-0-step_number": "1",
            "steps-0-description": "Updated step",
        }

        edit_response = self.client.post(edit_url, edit_data)
        self.assertEqual(edit_response.status_code, 302)

        # Verify changes
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, "Updated Recipe")
        self.assertEqual(recipe.ingredients.count(), 2)

        # 5. Delete recipe
        delete_url = reverse("recipes:recipe_delete", kwargs={"slug": recipe.slug})
        delete_response = self.client.post(delete_url)
        self.assertEqual(delete_response.status_code, 302)

        # Verify deletion
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_user_interaction_workflow(self):
        """Test: User interacts with another user's recipe"""

        # Create two users
        creator = User.objects.create_user(
            username="creator", email="creator@example.com", password="pass123"
        )
        interactor = User.objects.create_user(
            username="interactor", email="interactor@example.com", password="pass123"
        )

        # Creator makes a recipe
        recipe = Recipe.objects.create(
            title="Test Recipe",
            description="For interaction testing",
            creator=creator,
            prep_time=10,
            cook_time=5,
            servings=4,
        )

        # Interactor logs in
        self.client.login(username="interactor", password="pass123")

        # 1. Like the recipe
        like_url = reverse("recipes:toggle_like", kwargs={"recipe_id": recipe.id})
        like_response = self.client.post(like_url)
        self.assertEqual(like_response.status_code, 302)
        self.assertEqual(recipe.likes.count(), 1)

        # 2. Bookmark the recipe
        bookmark_url = reverse(
            "recipes:toggle_bookmark", kwargs={"recipe_id": recipe.id}
        )
        bookmark_response = self.client.post(bookmark_url)
        self.assertEqual(bookmark_response.status_code, 302)
        self.assertEqual(recipe.bookmarks.count(), 1)

        # 3. Rate the recipe
        rate_url = reverse("recipes:rate_recipe", kwargs={"recipe_id": recipe.id})
        rate_response = self.client.post(rate_url, {"value": 5})
        self.assertEqual(rate_response.status_code, 302)
        self.assertEqual(recipe.ratings.count(), 1)
        self.assertEqual(recipe.average_rating, 5.0)

        # 4. Comment on the recipe
        comment_url = reverse("recipes:add_comment", kwargs={"recipe_id": recipe.id})
        comment_response = self.client.post(comment_url, {"content": "Great recipe!"})
        self.assertEqual(comment_response.status_code, 302)
        self.assertEqual(recipe.comments.count(), 1)

        # 5. View recipe detail to see all interactions
        detail_url = reverse("recipes:recipe_detail", kwargs={"slug": recipe.slug})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "1")  # Like count
        self.assertContains(detail_response, "5.0")  # Rating
        self.assertContains(detail_response, "Great recipe!")  # Comment
