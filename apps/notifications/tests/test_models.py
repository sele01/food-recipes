from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from notifications.models import Activity
from recipes.models import Recipe, Comment

User = get_user_model()


class ActivityModelTests(TestCase):
    """Test Activity model"""

    def setUp(self):
        self.user = User.objects.create_user(username="actor", email='user@exa.com', password='password')
        self.recipient = User.objects.create_user(username="recipient", email='reci@exa.com', password='password')

        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            creator=self.recipient,
            prep_time=10,
            cook_time=5,
            servings=4,
        )

    def test_activity_creation(self):
        activity = Activity.objects.create(
            actor=self.user, verb="like", target=self.recipe, recipient=self.recipient
        )

        self.assertEqual(activity.actor, self.user)
        self.assertEqual(activity.verb, "like")
        self.assertEqual(activity.target, self.recipe)
        self.assertEqual(activity.recipient, self.recipient)
        self.assertFalse(activity.is_read)

    def test_activity_str(self):
        activity = Activity.objects.create(
            actor=self.user,
            verb="comment",
            target=self.recipe,
            recipient=self.recipient,
        )
        self.assertTrue(str(activity).startswith(f"{self.user} comment"))

    def test_activity_ordering(self):
        activity1 = Activity.objects.create(
            actor=self.user, verb="like", target=self.recipe, recipient=self.recipient
        )
        activity2 = Activity.objects.create(
            actor=self.user,
            verb="comment",
            target=self.recipe,
            recipient=self.recipient,
        )

        activities = Activity.objects.all()
        self.assertEqual(activities[0], activity2)  # Newest first

    def test_unread_filter(self):
        activity1 = Activity.objects.create(
            actor=self.user, verb="like", target=self.recipe, recipient=self.recipient
        )
        activity2 = Activity.objects.create(
            actor=self.user,
            verb="comment",
            target=self.recipe,
            recipient=self.recipient,
            is_read=True,
        )

        unread = Activity.objects.filter(is_read=False)
        self.assertIn(activity1, unread)
        self.assertNotIn(activity2, unread)

    def test_recipient_filter(self):
        other_user = User.objects.create_user(username="other")

        activity1 = Activity.objects.create(
            actor=self.user, verb="like", target=self.recipe, recipient=self.recipient
        )
        activity2 = Activity.objects.create(
            actor=self.user, verb="comment", target=self.recipe, recipient=other_user
        )

        recipient_activities = Activity.objects.filter(recipient=self.recipient)
        self.assertIn(activity1, recipient_activities)
        self.assertNotIn(activity2, recipient_activities)

    def test_generic_foreign_key_to_recipe(self):
        activity = Activity.objects.create(
            actor=self.user, verb="create", target=self.recipe, recipient=None
        )

        self.assertEqual(activity.target, self.recipe)
        self.assertEqual(
            activity.target_content_type, ContentType.objects.get_for_model(Recipe)
        )
        self.assertEqual(activity.target_object_id, self.recipe.id)

    def test_generic_foreign_key_to_comment(self):
        comment = Comment.objects.create(
            recipe=self.recipe, user=self.user, content="Test comment"
        )

        activity = Activity.objects.create(
            actor=self.user, verb="comment", target=comment, recipient=self.recipient
        )

        self.assertEqual(activity.target, comment)
        self.assertEqual(
            activity.target_content_type, ContentType.objects.get_for_model(Comment)
        )
        self.assertEqual(activity.target_object_id, comment.id)
