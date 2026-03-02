from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notifications.models import Activity
from recipes.models import Recipe

User = get_user_model()


class NotificationsListViewTests(TestCase):
    """Test the notifications list view"""

    def setUp(self):
        self.recipient = User.objects.create_user(
            username="recipient", email="recipient@example.com", password="testpass123"
        )
        self.actor = User.objects.create_user(
            username="actor", email="actor@example.com", password="testpass123"
        )

        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            creator=self.actor,
            prep_time=10,
            cook_time=5,
            servings=4,
        )

        # Create notifications
        for i in range(3):
            Activity.objects.create(
                actor=self.actor,
                verb="like",
                target=self.recipe,
                recipient=self.recipient,
                is_read=False,
            )

    def test_notifications_list_requires_login(self):
        url = reverse("notifications:list")  # Updated name
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_notifications_list_loads_for_logged_in_user(self):
        self.client.login(username="recipient", password="testpass123")
        url = reverse("notifications:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notifications/notifications_list.html")

    def test_notifications_marked_as_read_when_viewed(self):
        self.client.login(username="recipient", password="testpass123")
        url = reverse("notifications:list")
        self.client.get(url)

        # All notifications should be read
        unread = Activity.objects.filter(recipient=self.recipient, is_read=False)
        self.assertEqual(unread.count(), 0)


class MarkNotificationReadViewTests(TestCase):
    """Test the mark notification as read view"""

    def setUp(self):
        self.recipient = User.objects.create_user(
            username="recipient", email="recipient@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@example.com", password="testpass123"
        )
        self.actor = User.objects.create_user(
            username="actor", email="actor@example.com", password="testpass123"
        )

        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            creator=self.actor,
            prep_time=10,
            cook_time=5,
            servings=4,
        )

        self.notification = Activity.objects.create(
            actor=self.actor,
            verb="like",
            target=self.recipe,
            recipient=self.recipient,
            is_read=False,
        )

    def test_mark_read_requires_login(self):
        url = reverse(
            "notifications:mark_read", kwargs={"notification_id": self.notification.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_can_mark_own_notification_as_read(self):
        self.client.login(username="recipient", password="testpass123")
        url = reverse(
            "notifications:mark_read", kwargs={"notification_id": self.notification.id}
        )
        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_cannot_mark_others_notification_as_read(self):
        self.client.login(username="other", password="testpass123")
        url = reverse(
            "notifications:mark_read", kwargs={"notification_id": self.notification.id}
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.notification.refresh_from_db()
        self.assertFalse(self.notification.is_read)

    def test_mark_read_redirects_to_list(self):
        self.client.login(username="recipient", password="testpass123")
        url = reverse(
            "notifications:mark_read", kwargs={"notification_id": self.notification.id}
        )
        response = self.client.post(url)

        self.assertRedirects(response, reverse("notifications:list"))

    def test_mark_read_requires_post(self):
        self.client.login(username="recipient", password="testpass123")
        url = reverse(
            "notifications:mark_read", kwargs={"notification_id": self.notification.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        self.notification.refresh_from_db()
        self.assertFalse(self.notification.is_read)
