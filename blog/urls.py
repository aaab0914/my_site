
from django.urls import path
from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'

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
    )
]
