from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's built-in User.
    Email is required and unique.
    """
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=False,
        null=False,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    
    # Optional profile fields (add later if needed)
    # bio = models.TextField(_('bio'), max_length=500, blank=True)
    # profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')