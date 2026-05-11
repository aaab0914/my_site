# my_site/urls.py
# ========================================
# Imports
# ========================================

from django.contrib import admin
# admin: Django's built-in administration module

from django.urls import path, include
# path: Function for defining URL patterns
# include: Function for including other URL configurations

from django.contrib.sitemaps.views import sitemap
# sitemap: View function for generating sitemap XML

from markdownx import urls as markdownx_urls
# markdownx_urls: URL patterns for markdownx

from blog.sitemaps import PostSitemap
# PostSitemap: Sitemap class for Post model


# ========================================
# Sitemap Configuration
# ========================================

sitemaps = {
    'posts': PostSitemap,
}


# ========================================
# URL Patterns
# ========================================

urlpatterns = [
    # Admin interface
    path(
        "admin/",
        admin.site.urls
    ),

    # Blog application URLs
    path(
        'blog/',
        include('blog.urls', namespace='blog')
    ),

    # Sitemap
    path(
        'sitemap.xml'
        ,sitemap,
        {'sitemaps': sitemaps},
        name='django/contrib.sitemaps.views.sitemaps'
    ),

    # Markdownx URLs (for live preview)
    path(
        'markdownx/',
        include(markdownx_urls)
    ),
    # path(
    #     'accounts/',
    #     include('django.contrib.auth.urls')),
#     path(
#
#     )
]