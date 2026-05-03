from django.db import models
# models: Django's ORM module for defining database models

from django.utils import timezone
# timezone: Utility for handling timezone-aware datetime operations

from django.conf import settings
# settings: Access to Django project configuration settings (e.g., AUTH_USER_MODEL)

from django.urls import reverse
# reverse: Function to generate URLs by resolving view names and parameters

from taggit.managers import TaggableManager
# TaggableManager: Manager for handling tags on models (from django-taggit)

from django.utils.text import slugify
# slugify: Function to convert a string into a URL-friendly slug (e.g., "Hello World" → "hello-world")


# Custom manager class: Filters only published posts
class PublishedManager(models.Manager):
    # Override get_queryset to return only posts with PUBLISHED status
    def get_queryset(self):
        return (
            super().get_queryset().filter(status=Post.Status.PUBLISHED)
        )


# Post model class: Defines the data structure and behavior of blog posts
class Post(models.Model):

    # Inner enum class: Defines post status options (Draft / Published)
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(
        max_length=250,
        unique_for_date='publish'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10,
        choices=Status,
        default=Status.DRAFT
    )

    tags = TaggableManager()

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

    # Returns the absolute URL for the post detail page
    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug
            ]
        )

    # Override save method to automatically generate slug if not provided
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# Comment model class: Defines comments associated with blog posts
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    # Returns a human-readable string representation of the comment
    def __str__(self):
        return f"Comment by {self.name} on {self.post}"