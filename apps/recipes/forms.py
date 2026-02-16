from django import forms
from .models import Recipe, Ingredient, Step, RecipeImage


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "title",
            "description",
            "category",
            "prep_time",
            "cook_time",
            "servings",
            "featured_image",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ["name", "quantity", "unit"]


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ["step_number", "description", "image"]
