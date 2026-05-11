# users/admin.py
# ========================================
# Imports
# ========================================

from django.contrib import admin
# admin: Django's built-in administration interface module

from django.contrib.auth.admin import UserAdmin
# UserAdmin: The default admin configuration for the User model

from django.contrib.auth.models import User
# User: The built-in user model

from .models import Profile
# Profile: The user profile model (extends the built-in User model)


# ========================================
# Admin Configuration
# ========================================

class ProfileInline(admin.StackedInline):
    """
    Inline admin configuration for the Profile model.
    Displays the Profile fields inside the User admin page.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for the User model.
    Includes the Profile inline.
    """
    inlines = [ProfileInline]


# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)