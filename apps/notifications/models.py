from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class Activity(models.Model):
    """
    Tracks all user activities across the site
    """

    ACTIVITY_TYPES = [
        ("like", "Liked a recipe"),
        ("comment", "Commented on a recipe"),
        ("create", "Created a recipe"),
        ("bookmark", "Bookmarked a recipe"),
        ("follow", "Started following"),
        ("rate", "Rated a recipe"),
    ]

    # Who did the action
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activities"
    )

    # What action they did
    verb = models.CharField(max_length=50, choices=ACTIVITY_TYPES)

    # What they did it to (recipe, comment, etc.)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey("target_content_type", "target_object_id")

    # Optional: who receives this (for notifications)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )

    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name_plural = "Activities"
        app_label = 'notifications'

    def __str__(self):
        return f"{self.actor} {self.verb} {self.target}"
