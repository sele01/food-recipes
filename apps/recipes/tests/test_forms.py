from django.test import TestCase
from recipes.models import Category
from recipes.forms import RecipeForm


class RecipeFormTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Breakfast", slug="breakfast")

    def test_valid_form(self):
        form_data = {
            "title": "Test Recipe",
            "description": "Test description",
            "category": self.category.id,
            "prep_time": 10,
            "cook_time": 5,
            "servings": 4,
        }
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid())
