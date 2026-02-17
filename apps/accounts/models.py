from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's built-in User.
    Email is required and unique.
    """

    email = models.EmailField(
        _("email address"),
        unique=True,
        blank=False,
        null=False,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    # Additional fields can be added here as needed, for example:
    # New profile fields
    bio = models.TextField(
        _("bio"), max_length=500, blank=True
    )  # short biography or description of the user

    # profile picture field to allow users to upload a profile image
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # timestamp for when the user account was created
    updated_at = models.DateTimeField(
        auto_now=True
    )  # timestamp for when the user account

    def __str__(self):
        return self.username

    # helper method to count user's recipes
    def recipe_count(self):
        return self.recipes.count()
    
    

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
