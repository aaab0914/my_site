# images/models.py
# ========================================
# Imports
# ========================================

from django.db import models
# models: Django's ORM module for defining database models

from django.contrib.auth.models import User
# User: The built-in user model

from django.urls import reverse
# reverse: Function for generating URLs by resolving view names and parameters


# ========================================
# Models
# ========================================

class Image(models.Model):
    """
    Model for managing uploaded images.
    """
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images/%Y/%m/%d/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title