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

class LatestPostsFeed(Feed):

    title = 'My Blog'
    link = reverse_lazy('blog:post_list')
    description = 'New Posts of My Blog.'

    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        # 先将 Markdown 转换为 HTML，然后移除所有 HTML 标签
        plain_text = strip_tags(item.get_markdown_body())
        # 截断为 30 个单词，末尾添加省略号
        return truncatewords(plain_text, 30) + '...'

    def item_pubdate(self, item):
        return item.publish