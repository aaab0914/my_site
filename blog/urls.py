# urls.py
# ========================================
# Imports
# ========================================

from django.urls import path, include
# path: Function for defining URL patterns in Django

from . import views
# views: The views module containing all view functions for the blog app

from .feeds import LatestPostsFeed
# LatestPostsFeed: The RSS feed class for the blog
from .views import PostDeleteView


# ========================================
# App Namespace
# ========================================

app_name = 'blog'
# app_name: Namespace for the blog app's URLs


# ========================================
# URL Patterns
# ========================================

urlpatterns = [
    # URL pattern for displaying a single post detail page
    # Uses year, month, day, and slug to uniquely identify a post
    # Example: /2026/5/3/django-intro/
    path(
        '<int:year>/<int:month>/<int:day>/<slug:post_slug>/',
        views.post_detail,
        name='post_detail'
    ),

    # (Commented out) Alternative class-based view for post list
    # path('', views.PostListView.as_view(), name='post_list'),

    # URL pattern for handling comment submission on a specific post
    # Uses post_id to identify which post the comment belongs to
    # Example: /1/comment/ (1 is the post ID)
    path(
        '<int:post_id>/comment/',
        views.post_comment,
        name='post_comment'
    ),

    # URL pattern for displaying posts filtered by a specific tag
    # Uses tag_slug to identify which tag to filter by
    # Example: /tag/django/
    path(
        'tag/<slug:tag_slug>/',
        views.post_list,
        name='post_list_by_tag'
    ),

    # URL pattern for the main blog homepage showing all posts
    # Example: / (root path of the blog app)
    path(
        '',
        views.post_list,
        name='post_list'
    ),

    # URL pattern for the RSS feed of latest posts
    # Example: /feed/
    path(
        'feed/',
        LatestPostsFeed(),
        name='post_feed'
    ),

    # URL pattern for searching posts by keyword
    # Example: /search/
    path(
        'search/',
        views.post_search,
        name='post_search'
    ),

    # URL pattern for creating a new post
    # Example: /create/
    path(
        'create/',
        views.post_create,
        name='post_create'
    ),
    # 正确写法
    path(
        '<int:pk>/delete/',
        PostDeleteView.as_view(),
        name='post_delete'
    ),
    path(
        'post_delete_success/',
        views.post_delete_success,
        name='post_delete_success'
    ),
    # path(
    #     'accounts/',
    #     include('django.contrib.auth.urls')
    # ),
    # path(
    #     'comment_delete/',
    #     CommentDeleteView.as_view(),
    #     name='comment_delete'
    # ),
    # path(
    #     'add_comment/',
    #     views.add_comment,
    #     name='add_comment'
    # ),
]