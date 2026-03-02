from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Follow
from recipes.models import Recipe, Like


User = get_user_model()


class ProfileViewTests(TestCase):
    """Test profile views"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            bio="Original bio",
        )

        self.other_user = User.objects.create_user(
            username="other", email="other@example.com", password="testpassword"
        )

    def test_profile_view_loads(self):
        """Test that profile page loads"""
        url = reverse("accounts:profile", kwargs={"username": "testuser"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        self.assertContains(response, "testuser")
        self.assertContains(response, "Original bio")

    def test_profile_view_404_for_nonexistent_user(self):
        """Test that non-existent user returns 404"""
        url = reverse("accounts:profile", kwargs={"username": "nonexistent"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_profile_shows_correct_stats(self):
        """Test that profile shows correct recipe counts"""

        # Create recipes
        recipe1 = Recipe.objects.create(
            title="Recipe1",
            description="Test",
            creator=self.user,
            prep_time=10,
            cook_time=5,
            servings=4,
        )
        recipe2 = Recipe.objects.create(
            title="Recipe2",
            description="Test",
            creator=self.user,
            prep_time=10,
            cook_time=5,
            servings=4,
        )

        # Add likes
        Like.objects.create(recipe=recipe1, user=self.other_user)
        Like.objects.create(recipe=recipe2, user=self.other_user)

        url = reverse("accounts:profile", kwargs={"username": "testuser"})
        response = self.client.get(url)


        self.assertContains(response, "2")
        self.assertContains(response, "Recipes")

        self.assertContains(response, "2")
        self.assertContains(response, "Likes")


class DashboardViewTests(TestCase):
    """Test dashboard views"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

    def test_dashboard_requires_login(self):
        """Test that dashboard redirects anonymous users"""
        url = reverse("accounts:dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_dashboard_loads_for_logged_in_user(self):
        """Test that logged-in users can access dashboard"""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("accounts:dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/dashboard.html")

    def test_dashboard_update_profile(self):
        """Test that users can update their profile"""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("accounts:dashboard")

        response = self.client.post(
            url,
            {
                "username": "testuser",
                "email": "test@example.com",
                "bio": "Updated bio",
                "website": "https://newwebsite.com",
            },
        )

        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Check that profile was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "Updated bio")
        self.assertEqual(self.user.website, "https://newwebsite.com")


class FollowViewTests(TestCase):
    """Test follow/unfollow functionality"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpassword"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpassword"
        )

    def test_follow_user(self):
        """Test following another user"""
        self.client.login(username="user1", password="testpassword")
        url = reverse("accounts:toggle_follow", kwargs={"username": "user2"})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)  # Redirect to profile

        # Check follow was created
        self.assertTrue(
            Follow.objects.filter(follower=self.user1, followed=self.user2).exists()
        )

    def test_unfollow_user(self):
        """Test unfollow a user"""
        # First follow
        Follow.objects.create(follower=self.user1, followed=self.user2)

        self.client.login(username="user1", password="testpassword")
        url = reverse("accounts:toggle_follow", kwargs={"username": "user2"})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Check follow was removed
        self.assertFalse(
            Follow.objects.filter(follower=self.user1, followed=self.user2).exists()
        )

    def test_cannot_follow_self(self):
        """Test that users cannot follow themselves"""
        self.client.login(username="user1", password="testpassword")
        url = reverse("accounts:toggle_follow", kwargs={"username": "user1"})
        response = self.client.post(url)

        # Should redirect with error message
        self.assertEqual(response.status_code, 302)

        # Check no follow created
        self.assertFalse(
            Follow.objects.filter(follower=self.user1, followed=self.user1).exists()
        )
