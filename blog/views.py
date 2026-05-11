# views.py
# ========================================
# 导入部分
# ========================================
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
# render: Renders a template with a context dictionary
# get_object_or_404: Retrieves an object or raises a 404 error if not found
# redirect: Redirects to a specific URL

from django.http import Http404
# Http404: Exception class for raising 404 errors (e.g., when an object doesn't exist)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Paginator: Splits a queryset into pages for pagination
# EmptyPage: Exception raised when accessing a page outside the valid range
# PageNotAnInteger: Exception raised when the page number is not an integer

from django.views.generic import ListView
# ListView: Class-based view for displaying a list of objects

# from django.conf import settings
# from django.contrib.redirects.models import Redirect

from django.views.decorators.http import require_POST
# require_POST: Decorator that restricts a view to accept only POST requests

from django.db.models import Count
from django.views.generic.detail import DetailView
# Count: Aggregation function used to count the number of related objects

from taggit.models import Tag
# Tag: Model class representing tags used for tagging posts

from .models import Post, Comment
# Post: The main blog post model (imported from the current app)

from .forms import EmailPostForm, CommentForm, SearchForm, PostCreateForm
# EmailPostForm: Form for sharing a post via email
# CommentForm: Form for adding a comment to a post
# SearchForm: Form for searching posts by keyword
# PostCreateForm: Form for creating a new post

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
# SearchVector: Represents a searchable document composed of fields (e.g., title + body)
# SearchQuery: Represents a search query expression (e.g., 'django')
# SearchRank: Calculates a rank for search results based on relevance
# TrigramSimilarity: PostgreSQL trigram similarity function for fuzzy text matching

from django.db.models import Q
# Q: Used to build complex queries with OR, AND, and NOT conditions

from django.contrib.auth.decorators import login_required
# login_required: Decorator that restricts a view to authenticated users only

from django.utils.text import slugify
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView


# slugify: Converts a string into a URL-friendly slug


# ========================================
# 类视图
# ========================================

class PostListView(ListView):
    """
    Class-based view for listing posts (alternative implementation to function-based post_list).

    This view automatically:
    - Queries Post.published.all() (only published posts)
    - Paginates results (10 posts per page)
    - Passes 'posts' as context variable to template
    - Uses 'blog/post/list.html' template

    URL pattern example: path('', PostListView.as_view(), name='post_list')
    """

    # QuerySet to retrieve only published posts (using custom manager)
    # Post.published is a custom manager that filters status=PUBLISHED
    queryset = Post.published.all()

    # Name of the context variable available in the template
    # Template will use {% for post in posts %} instead of {% for post in object_list %}
    context_object_name = 'posts'

    # Number of posts to display per page
    # Creates pagination with 10 posts on each page
    paginate_by = 10

    # Template file used to render the list of posts
    template_name = 'blog/post/list.html'


# ========================================
# 函数视图
# ========================================

def post_share(request, post_id):
    """
    View function for sharing a post via email.

    This view:
    - Retrieves a published post by its ID
    - Displays a form for entering recipient email and comments (GET request)
    - Processes the form and sends an email (POST request)

    Note: The actual email sending logic is omitted (commented out).

    :param request: HTTP request object
    :param post_id: Primary key of the post to share
    :return: Rendered share form or redirect after successful email
    """

    # Retrieve the post by ID, ensuring it's published
    # Returns 404 if post doesn't exist or is not published
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    # Handle POST request (form submission)
    if request.method == 'POST':
        # Bind form with submitted POST data
        form = EmailPostForm(request.POST)

        # Validate the form (check required fields, email format, etc.)
        if form.is_valid():
            # Get cleaned data from the form (sanitized and validated)
            cd = form.cleaned_data

            # ... send email logic would go here
            # Typically: send_mail(subject, message, from_email, [to_email])
            # The actual implementation is omitted/commented out in this code

    else:
        # GET request: display empty form
        form = EmailPostForm()

    # Render the share template with post and form
    return render(
        request,
        'blog/post/share.html',
        {'post': post, 'form': form}
    )


def post_list(request, tag_slug=None):
    """
    View function for displaying a list of posts with optional tag filtering.

    Features:
    - Shows only published posts
    - Supports filtering by tag slug (optional URL parameter)
    - Paginates results (10 posts per page)
    - Handles invalid page numbers gracefully

    URL patterns:
        /blog/              - Shows all posts
        /blog/tag/django/   - Shows posts tagged with 'django'

    :param request: HTTP request object
    :param tag_slug: Optional slug of the tag to filter by (from URL)
    :return: Rendered list template with posts and optional tag
    """

    # Start with all published posts
    post_list = Post.published.all()

    # Variable to store the tag object (if filtering by tag)
    tag = None

    # Check if a tag slug was provided in the URL
    if tag_slug:
        # Retrieve the tag object by its slug, or return 404 if not found
        tag = get_object_or_404(Tag, slug=tag_slug)

        # Filter posts to only those that have this tag
        # tags__in=[tag] checks if the post's tags contain this tag
        post_list = post_list.filter(tags__in=[tag])

    # Initialize paginator with 10 posts per page
    paginator = Paginator(post_list, 10)

    # Get the page number from request GET parameters (default to page 1)
    page_number = request.GET.get('page', 1)

    try:
        # Get the Page object for the requested page number
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page number is not an integer (e.g., 'abc'), return first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page number is out of range (e.g., beyond last page), return last page
        posts = paginator.page(paginator.num_pages)

    # Render the template with posts and tag (None if no tag filtering)
    return render(
        request,
        'blog/post/list.html',
        {'posts': posts, 'tag': tag if tag_slug else None}
    )


def post_detail(request, year, month, day, post_slug):
    """
    View function for displaying a single post detail page.

    This view:
    - Retrieves a published post by slug and publication date
    - Displays active comments for the post
    - Provides a form for adding new comments
    - Shows similar posts based on tag overlap and title similarity

    URL pattern: /blog/2024/01/15/my-post-slug/

    :param request: HTTP request object
    :param year: Publication year (e.g., 2024)
    :param month: Publication month (e.g., 1 for January)
    :param day: Publication day (e.g., 15)
    :param post_slug: URL-friendly slug of the post (e.g., 'my-post-slug')
    :return: Rendered detail template with post, comments, form, and similar posts
    """

    # Retrieve the published post matching all criteria
    # This ensures the URL (with date and slug) uniquely identifies the post
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,  # Only published posts
        slug=post_slug,  # Match the slug
        publish__year=year,  # Match publication year
        publish__month=month,  # Match publication month
        publish__day=day  # Match publication day
    )

    # Get all active comments for this post (approved comments only)
    comments = post.comments.filter(active=True)

    # Create an empty comment form for user input
    form = CommentForm()

    # Get list of tag IDs associated with this post
    # values_list('id', flat=True) returns a flat list like [1, 2, 3] instead of [(1,), (2,), (3,)]
    post_tags_ids = post.tags.values_list('id', flat=True)

    # --- Find similar posts based on shared tags ---
    # Query posts that share at least one tag with the current post
    tag_based_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(id=post.id)  # Exclude the current post itself

    # --- Initialize empty queryset for title-based similar posts ---
    title_based_posts = Post.published.none()

    # If tag-based results are fewer than 4, supplement with title similarity
    if tag_based_posts.count() < 4:
        # Use PostgreSQL trigram similarity to find posts with similar titles
        title_based_posts = Post.published.annotate(
            similarity=TrigramSimilarity('title', post.title)
        ).filter(
            similarity__gt=0.1  # Only posts with >10% title similarity
        ).exclude(
            id=post.id
        ).order_by('-similarity')[:4 - tag_based_posts.count()]  # Take only what's needed

    # Combine tag-based and title-based results, removing duplicates
    similar_posts = (tag_based_posts | title_based_posts).distinct()

    # Annotate with count of common tags and order by relevance
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')  # Count how many tags are shared
    ).order_by(
        '-same_tags',  # Posts with more shared tags come first
        '-publish'  # Then by newest publication date
    )[:4]  # Limit to maximum 4 similar posts

    # Render the detail template with all context data
    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
            'similar_posts': similar_posts
        }
    )


@require_POST
def post_comment(request, post_id):
    """
    View function for handling comment submission (POST only).

    This view:
    - Accepts only POST requests (decorated with @require_POST)
    - Creates a new comment for the specified post
    - Associates the comment with the post (foreign key)
    - Comments are created with active=False by default (requires moderation)

    :param request: HTTP request object (must be POST)
    :param post_id: Primary key of the post to comment on
    :return: Rendered comment template with post, form, and new comment
    """

    # Retrieve the published post by ID
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    # Initialize comment variable (None if no comment created yet)
    comment = None

    # Create a form instance with the submitted POST data
    form = CommentForm(data=request.POST)

    # Validate the form (check required fields, etc.)
    if form.is_valid():
        # Create a comment object without saving to database yet
        comment = form.save(commit=False)

        # Associate the comment with the post
        comment.post = post

        # Save the comment to database (active=False by default, pending moderation)
        comment.save()

    # Render the comment template with context
    return render(
        request,
        'blog/post/templates/blog/comment/comment.html',
        {'post': post, 'form': form, 'comment': comment}
    )


def post_search(request):
    """
    View function for searching posts by keyword using PostgreSQL full-text search.

    This view implements hybrid search combining:
    1. PostgreSQL full-text search (ranked by relevance)
    2. Trigram similarity (fuzzy matching for typos)

    Features:
    - Searches both title (weight A) and body (weight B)
    - Combines full-text and trigram results
    - Orders results by final relevance rank

    URL pattern: /blog/search/?query=django

    :param request: HTTP request object (with optional 'query' GET parameter)
    :return: Rendered search template with form, query, and results
    """

    # Initialize empty form, query, and results
    form = SearchForm()
    query = None
    results = []

    # Check if 'query' parameter is present in the URL
    if 'query' in request.GET:
        # Bind form with GET data (search is typically a GET request)
        form = SearchForm(request.GET)

        # Validate the form (ensures query is not empty)
        if form.is_valid():
            # Get the sanitized search query
            query = form.cleaned_data['query']

            # --- Full-Text Search with Ranking ---
            # Create a search vector: title (weight A) + body (weight B)
            # Weight A is more important than weight B
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')

            # Create a search query from the user's input
            search_query = SearchQuery(query)

            # Annotate posts with relevance rank and filter by minimum rank
            full_text_results = Post.published.annotate(
                rank=SearchRank(search_vector, search_query)
            ).filter(
                rank__gte=0.1  # Only posts with relevance > 10%
            ).order_by(
                '-rank',  # Most relevant first
                '-publish'  # Then newest first
            )

            # --- Trigram (Fuzzy) Search for typos and partial matches ---
            trigram_results = Post.published.annotate(
                title_similarity=TrigramSimilarity('title', query),
                body_similarity=TrigramSimilarity('body', query),
                # Combined similarity: title counts twice as much as body
                total_similarity=(
                        TrigramSimilarity('title', query) * 2 +
                        TrigramSimilarity('body', query)
                )
            ).filter(
                # Match if either title OR body has sufficient similarity
                Q(title_similarity__gt=0.1) | Q(body_similarity__gt=0.1)
            ).order_by(
                '-total_similarity',  # Most similar first
                '-publish'  # Then newest first
            )

            # --- Combine both search methods ---
            # Union of full-text and trigram results (no duplicates)
            combined_results = (full_text_results | trigram_results).distinct()

            # Final annotation with combined ranking
            results = combined_results.annotate(
                final_rank=SearchRank(search_vector, search_query) + (TrigramSimilarity('title', query) * 2)
            ).order_by(
                '-final_rank',  # Most relevant overall
                '-publish'  # Then newest first
            )

    # Render search template with results
    return render(
        request,
        'blog/post/search.html',
        {'form': form, 'query': query, 'results': results}
    )


@login_required
def post_create(request):
    """
    View function for creating a new post (authenticated users only).

    This view:
    - Requires user to be logged in (@login_required decorator)
    - Displays an empty form for GET requests
    - Processes form submission for POST requests
    - Automatically sets the author to the current logged-in user
    - Automatically publishes the post (status set to PUBLISHED)

    Note: This is an admin/create view, not part of the public blog.

    :param request: HTTP request object
    :return: Rendered create form or redirect to the new post's detail page
    """

    # Handle POST request (form submission)
    if request.method == 'POST':
        # Bind form with POST data
        form = PostCreateForm(request.POST)

        # Validate the form
        if form.is_valid():
            # Create post object without saving to DB yet
            post = form.save(commit=False)

            # Set the author to the currently logged-in user
            # This prevents users from impersonating others
            post.author = request.user

            # Set status to PUBLISHED (immediately visible)
            # Could be changed to DRAFT for review workflow
            post.status = Post.Status.PUBLISHED

            # Save the post to database (now with author and status)
            post.save()

            # Save many-to-many relationships (tags)
            # Must be called after the post has a primary key
            form.save_m2m()

            # Redirect to the newly created post's detail page
            return redirect(post.get_absolute_url())

    else:
        # GET request: display empty form
        form = PostCreateForm()

    # Render the create post template
    return render(request, 'blog/post/create.html', {'form': form})


def post_delete_success(request):
    return render(request, 'blog/post/post_delete_successful.html')

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post/post_delete.html'
    success_url = reverse_lazy('blog:post_delete_success')
    context_object_name = 'post'
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user and not request.user.is_superuser:
            raise PermissionDenied("You are not allowed to delete this post.")
        return super().dispatch(request, *args, **kwargs)

    # def delete(self, request, *args, **kwargs):
    #     """
    #     重写 delete 方法，确保删除操作被执行。
    #     """
    #     obj = self.get_object()
    #     obj.delete()
    #     return redirect(self.success_url)


# class ReturnHomePageView(Redirect):
#     model = Post
#     template_name = 'blog/post/.html'

# class CommentDeleteView(LoginRequiredMixin, DeleteView):
#     model = Comment
#     template_name = 'blog/post/delete_comment.html'


def add_comment(self, request, *args, **kwargs):
