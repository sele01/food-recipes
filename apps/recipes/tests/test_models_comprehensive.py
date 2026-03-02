from django.test import TestCase
from django.contrib.auth import get_user_model
from recipes.models import (
    Category,
    Recipe,
    RecipeImage,
    Ingredient,
    Step,
    Like,
    Comment,
    Bookmark,
    Rating,
    Collection,
    CollectionItem,
)

User = get_user_model()


class CategoryModelTests(TestCase):
    """Test Category model"""

    def setUp(self):
        self.category = Category.objects.create(name="Breakfast", slug="breakfast")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Breakfast")
        self.assertEqual(self.category.slug, "breakfast")

    def test_category_str(self):
        self.assertEqual(str(self.category), "Breakfast")

    def test_category_slug_auto_generated(self):
        category = Category.objects.create(name="Italian Food")
        self.assertEqual(category.slug, "italian-food")

    def test_category_ordering(self):
        Category.objects.create(name="Dinner", slug="dinner")
        Category.objects.create(name="Breakfast", slug="breakfast")

        categories = Category.objects.all()
        self.assertEqual(categories[0].name, "Breakfast")  # Alphabetical


class RecipeModelComprehensiveTests(TestCase):
    """Comprehensive Recipe model tests"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="chef", email="chef@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Dessert", slug="dessert")

        self.recipe = Recipe.objects.create(
            title="Chocolate Cake",
            description="Rich chocolate cake",
            creator=self.user,
            category=self.category,
            prep_time=20,
            cook_time=30,
            servings=8,
            slug="chocolate-cake",
            is_published=True,
        )

    def test_recipe_creation(self):
        self.assertEqual(self.recipe.title, "Chocolate Cake")
        self.assertEqual(self.recipe.creator, self.user)
        self.assertEqual(self.recipe.category, self.category)
        self.assertTrue(self.recipe.is_published)

    def test_recipe_str(self):
        self.assertEqual(str(self.recipe), "Chocolate Cake")

    def test_total_time_property(self):
        self.assertEqual(self.recipe.total_time, 50)  # 20 + 30

    def test_recipe_ordering(self):
        recipe2 = Recipe.objects.create(
            title="Vanilla Cake",
            creator=self.user,
            prep_time=15,
            cook_time=25,
            servings=6,
        )
        recipes = Recipe.objects.all()
        self.assertEqual(recipes[0], recipe2)  # Newest first? Check ordering

    def test_slug_uniqueness(self):
        with self.assertRaises(Exception):
            Recipe.objects.create(
                title="Another Cake",
                creator=self.user,
                prep_time=10,
                cook_time=20,
                servings=4,
                slug="chocolate-cake",  # Duplicate slug!
            )

    def test_is_published_filter(self):
        recipe2 = Recipe.objects.create(
            title="Secret Recipe",
            creator=self.user,
            prep_time=10,
            cook_time=20,
            servings=4,
            is_published=False,
        )

        published = Recipe.objects.filter(is_published=True)
        self.assertIn(self.recipe, published)
        self.assertNotIn(recipe2, published)


class IngredientModelTests(TestCase):
    """Test Ingredient model"""

    def setUp(self):
        self.user = User.objects.create_user(username="chef",email='test@example.com' , password='password')
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            creator=self.user,
            prep_time=10,
            cook_time=5,
            servings=4,
        )

    def test_ingredient_creation(self):
        ingredient = Ingredient.objects.create(
            recipe=self.recipe, name="Flour", quantity="2", unit="cups", order=1
        )

        self.assertEqual(ingredient.name, "Flour")
        self.assertEqual(ingredient.quantity, "2")
        self.assertEqual(ingredient.unit, "cups")
        self.assertEqual(ingredient.recipe, self.recipe)

    def test_ingredient_str(self):
        ingredient = Ingredient.objects.create(
            recipe=self.recipe, name="Sugar", quantity="1", unit="cup"
        )
        self.assertEqual(str(ingredient), "1 cup Sugar")

    def test_ingredient_str_without_unit(self):
        ingredient = Ingredient.objects.create(
            recipe=self.recipe, name="Eggs", quantity="3", unit=""
        )
        self.assertEqual(str(ingredient), "3  Eggs".strip())  # Should handle blank unit

    def test_ingredient_ordering(self):
        ing1 = Ingredient.objects.create(recipe=self.recipe, name="Flour", order=2)
        ing2 = Ingredient.objects.create(recipe=self.recipe, name="Sugar", order=1)

        ingredients = self.recipe.ingredients.all()
        self.assertEqual(ingredients[0], ing2)  # Lower order first


class StepModelTests(TestCase):
    """Test Step model"""

    def setUp(self):
        self.user = User.objects.create_user(username="chef", email='test@example.com', password='password')
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            creator=self.user,
            prep_time=10,
            cook_time=5,
            servings=4,
        )

    def test_step_creation(self):
        step = Step.objects.create(
            recipe=self.recipe, step_number=1, description="Mix ingredients"
        )

        self.assertEqual(step.step_number, 1)
        self.assertEqual(step.description, "Mix ingredients")
        self.assertEqual(step.recipe, self.recipe)

    def test_step_str(self):
        step = Step.objects.create(
            recipe=self.recipe, step_number=2, description="Bake for 30 minutes"
        )
        self.assertEqual(str(step), "Step 2")

    def test_step_ordering(self):
        step1 = Step.objects.create(
            recipe=self.recipe, step_number=2, description="Second"
        )
        step2 = Step.objects.create(
            recipe=self.recipe, step_number=1, description="First"
        )

        steps = self.recipe.steps.all()
        self.assertEqual(steps[0], step2)  # Lower step number first


class LikeModelTests(TestCase):
    """Test Like model"""

    def setUp(self):
        self.user = User.objects.create_user(username="user1", email='user1@example.com', password='user1pass')
        self.user2 = User.objects.create_user(username="user2", email='user2@example.com', password='user2pass')
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            creator=self.user,
            prep_time=10,
            cook_time=5,
            servings=4,
        )

    def test_like_creation(self):
        like = Like.objects.create(recipe=self.recipe, user=self.user2)

        self.assertEqual(like.recipe, self.recipe)
        self.assertEqual(like.user, self.user2)
        self.assertIsNotNone(like.created_at)

    def test_like_str(self):
        like = Like.objects.create(recipe=self.recipe, user=self.user2)
        self.assertEqual(str(like), f"{self.user2} likes {self.recipe}")

    def test_unique_like(self):
        """Test user can't like same recipe twice"""
        Like.objects.create(recipe=self.recipe, user=self.user2)

        with self.assertRaises(Exception):
            Like.objects.create(recipe=self.recipe, user=self.user2)

    def test_like_count(self):
        Like.objects.create(recipe=self.recipe, user=self.user2)

        user3 = User.objects.create_user(username="user3", email='user3@example.com', password='user3pass')
        Like.objects.create(recipe=self.recipe, user=user3)

        self.assertEqual(self.recipe.likes.count(), 2)

    def test_cascade_delete(self):
        """Test likes deleted when recipe deleted"""
        like = Like.objects.create(recipe=self.recipe, user=self.user2)
        like_id = like.id

        self.recipe.delete()

        with self.assertRaises(Like.DoesNotExist):
            Like.objects.get(id=like_id)


class CommentModelTests(TestCase):
    """Test Comment model"""

    def setUp(self):
        self.user = User.objects.create_user(username="commenter", email='comment@example.comm', password='commentpass')
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            creator=self.user,
            prep_time=10,
            cook_time=5,
            servings=4,
        )

    def test_comment_creation(self):
        comment = Comment.objects.create(
            recipe=self.recipe, user=self.user, content="Great recipe!"
        )

        self.assertEqual(comment.content, "Great recipe!")
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.recipe, self.recipe)

    def test_comment_str(self):
        comment = Comment.objects.create(
            recipe=self.recipe,
            user=self.user,
            content="This is a long comment that should be truncated...",
        )
        self.assertTrue(str(comment).startswith("Comment by commenter on"))

    def test_comment_ordering(self):
        comment1 = Comment.objects.create(
            recipe=self.recipe, user=self.user, content="First"
        )
        comment2 = Comment.objects.create(
            recipe=self.recipe, user=self.user, content="Second"
        )

        comments = self.recipe.comments.all()
        self.assertEqual(comments[0], comment2)  # Newest first


class BookmarkModelTests(TestCase):
    """Test Bookmark model"""

    def setUp(self):
        self.user = User.objects.create_user(username="saver", email='saver@example.com', password='saverpass')
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            creator=self.user,
            prep_time=10,
            cook_time=5,
            servings=4,
        )

    def test_bookmark_creation(self):
        bookmark = Bookmark.objects.create(recipe=self.recipe, user=self.user)

        self.assertEqual(bookmark.recipe, self.recipe)
        self.assertEqual(bookmark.user, self.user)

    def test_unique_bookmark(self):
        Bookmark.objects.create(recipe=self.recipe, user=self.user)

        with self.assertRaises(Exception):
            Bookmark.objects.create(recipe=self.recipe, user=self.user)


class RatingModelTests(TestCase):
    """Test Rating model"""

    def setUp(self):
        self.user = User.objects.create_user(username="rater", email='rater@example.com', password='saverpass')
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            creator=self.user,
            prep_time=10,
            cook_time=5,
            servings=4,
        )

    def test_rating_creation(self):
        rating = Rating.objects.create(recipe=self.recipe, user=self.user, value=5)

        self.assertEqual(rating.value, 5)
        self.assertEqual(rating.recipe, self.recipe)

    def test_rating_value_validation(self):
        with self.assertRaises(Exception):
            Rating.objects.create(
                recipe=self.recipe, user=self.user, value=6  # Invalid - should be 1-5
            )

        with self.assertRaises(Exception):
            Rating.objects.create(
                recipe=self.recipe, user=self.user, value=0  # Invalid
            )

    def test_unique_rating(self):
        Rating.objects.create(recipe=self.recipe, user=self.user, value=5)

        with self.assertRaises(Exception):
            Rating.objects.create(recipe=self.recipe, user=self.user, value=4)

    def test_update_rating(self):
        rating = Rating.objects.create(recipe=self.recipe, user=self.user, value=3)

        # Update rating
        rating.value = 5
        rating.save()

        self.assertEqual(rating.value, 5)


class CollectionModelTests(TestCase):
    """Test Collection model"""

    def setUp(self):
        self.user = User.objects.create_user(username="collector", email='collect@example.com', password='collectpass')
        self.recipe1 = Recipe.objects.create(
            title="Recipe 1", creator=self.user, prep_time=10, cook_time=5, servings=4
        )
        self.recipe2 = Recipe.objects.create(
            title="Recipe 2", creator=self.user, prep_time=10, cook_time=5, servings=4
        )

    def test_collection_creation(self):
        collection = Collection.objects.create(
            name="Favorites",
            description="My favorite recipes",
            creator=self.user,
            is_public=True,
        )

        self.assertEqual(collection.name, "Favorites")
        self.assertEqual(collection.creator, self.user)
        self.assertTrue(collection.is_public)

    def test_collection_str(self):
        collection = Collection.objects.create(name="Dinner Ideas", creator=self.user)
        self.assertEqual(str(collection), "Dinner Ideas by collector")

    def test_unique_collection_name_per_user(self):
        Collection.objects.create(name="Favorites", creator=self.user)

        with self.assertRaises(Exception):
            Collection.objects.create(name="Favorites", creator=self.user)

    def test_different_users_same_collection_name(self):
        user2 = User.objects.create_user(username="user2", email='user2@example.com', password='user2pass')

        Collection.objects.create(name="Favorites", creator=self.user)

        # This should work - different user
        collection2 = Collection.objects.create(name="Favorites", creator=user2)
        self.assertIsNotNone(collection2)

    def test_recipe_count_property(self):
        collection = Collection.objects.create(name="Favorites", creator=self.user)

        CollectionItem.objects.create(collection=collection, recipe=self.recipe1)
        CollectionItem.objects.create(collection=collection, recipe=self.recipe2)

        self.assertEqual(collection.recipe_count, 2)

    def test_private_collection(self):
        collection = Collection.objects.create(
            name="Private", creator=self.user, is_public=False
        )

        self.assertFalse(collection.is_public)


class CollectionItemModelTests(TestCase):
    """Test CollectionItem model"""

    def setUp(self):
        self.user = User.objects.create_user(username="collector", email='collect@example.com', password='collectpass')
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            creator=self.user,
            prep_time=10,
            cook_time=5,
            servings=4,
        )
        self.collection = Collection.objects.create(name="Favorites", creator=self.user)

    def test_collection_item_creation(self):
        item = CollectionItem.objects.create(
            collection=self.collection, recipe=self.recipe, notes="Love this!"
        )

        self.assertEqual(item.collection, self.collection)
        self.assertEqual(item.recipe, self.recipe)
        self.assertEqual(item.notes, "Love this!")

    def test_unique_item_per_collection(self):
        CollectionItem.objects.create(collection=self.collection, recipe=self.recipe)

        with self.assertRaises(Exception):
            CollectionItem.objects.create(
                collection=self.collection, recipe=self.recipe  # Duplicate!
            )

    def test_collection_item_str(self):
        item = CollectionItem.objects.create(
            collection=self.collection, recipe=self.recipe
        )
        self.assertEqual(str(item), f"{self.recipe.title} in {self.collection.name}")

    def test_cascade_delete_collection(self):
        item = CollectionItem.objects.create(
            collection=self.collection, recipe=self.recipe
        )
        item_id = item.id

        self.collection.delete()

        with self.assertRaises(CollectionItem.DoesNotExist):
            CollectionItem.objects.get(id=item_id)

    def test_cascade_delete_recipe(self):
        item = CollectionItem.objects.create(
            collection=self.collection, recipe=self.recipe
        )
        item_id = item.id

        self.recipe.delete()

        with self.assertRaises(CollectionItem.DoesNotExist):
            CollectionItem.objects.get(id=item_id)
