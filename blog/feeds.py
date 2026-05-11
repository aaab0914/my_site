# feeds.py
# ========================================
# Imports
# ========================================

import markdown
# markdown: Python library for converting Markdown text to HTML

from django.contrib.syndication.views import Feed
# Feed: Base class for creating RSS/Atom feeds in Django

from django.template.defaultfilters import truncatewords_html, truncatewords
# truncatewords_html: Template filter that truncates HTML text to a specified number of words
# truncatewords: Template filter that truncates plain text to a specified number of words

from django.urls import reverse_lazy
# reverse_lazy: Lazy version of reverse() for generating URLs when the URL configuration is not yet loaded

from .models import Post
# Post: The main blog post model (imported from the current app)

from django.utils.html import strip_tags
# strip_tags: Utility function to remove HTML tags from a string


# ========================================
# RSS Feed Class
# ========================================

class LatestPostsFeed(Feed):
    """
    RSS feed for the latest blog posts.
    """
    title = 'My Blog'
    link = reverse_lazy('blog:post_list')
    description = 'New Posts of My Blog.'

    def items(self):
        """
        Returns the latest 5 published posts.
        """
        return Post.published.all()[:5]

    def item_title(self, item):
        """
        Returns the title of a post.
        """
        return item.title

    def item_description(self, item):
        """
        Returns the description of a post (plain text, truncated to 30 words).
        """
        # Convert Markdown to HTML, then strip all HTML tags
        plain_text = strip_tags(item.get_markdown_body())
        # Truncate to 30 words and add ellipsis
        return truncatewords(plain_text, 30) + '...'

    def item_pubdate(self, item):
        """
        Returns the publication date of a post.
        """
        return item.publish