# users/models.py
# ========================================
# Imports
# ========================================

from django.db import models
# models: Django's ORM module for defining database models

from django.contrib.auth.models import User
# User: The built-in user model

from django.db.models.signals import post_save
# post_save: Signal that is sent after a model instance is saved

from django.dispatch import receiver
# receiver: Decorator for connecting a signal to a function


# ========================================
# Models
# ========================================

class Profile(models.Model):
    """
    Extension of the built-in User model with additional profile fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'


# ========================================
# Signals
# ========================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal function to create a Profile instance when a User is created.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal function to save the Profile instance when a User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()