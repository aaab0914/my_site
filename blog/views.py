from django.shortcuts import render, get_object_or_404
# render: Renders a template with a context dictionary
# get_object_or_404: Retrieves an object or raises a 404 error if not found

from django.http import Http404
# Http404: Exception class for raising 404 errors (e.g., when an object doesn't exist)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Paginator: Splits a queryset into pages for pagination
# EmptyPage: Exception raised when accessing a page outside the valid range
# PageNotAnInteger: Exception raised when the page number is not an integer

from django.views.generic import ListView
# ListView: Class-based view for displaying a list of objects

from django.views.decorators.http import require_POST
# require_POST: Decorator that restricts a view to accept only POST requests

from django.db.models import Count
# Count: Aggregation function used to count the number of related objects

from taggit.models import Tag
# Tag: Model class representing tags used for tagging posts

from .models import Post
# Post: The main blog post model (imported from the current app)

from .forms import EmailPostForm, CommentForm, SearchForm
# EmailPostForm: Form for sharing a post via email
# CommentForm: Form for adding a comment to a post
# SearchForm: Form for searching posts by keyword

from django.db.models import Count
# Count: Aggregation function used to count the number of related objects

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
# SearchVector: Represents a searchable document composed of fields (e.g., title + body)
# SearchQuery: Represents a search query expression (e.g., 'django')
# SearchRank: Calculates a rank for search results based on relevance
# TrigramSimilarity: PostgreSQL trigram similarity function for fuzzy text matching

from django.db.models import Q
# Q: Used to build complex queries with OR, AND, and NOT conditions


# Class-based view for listing posts (alternative implementation)
class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 10
    template_name = 'blog/post/list.html'

# View function for sharing a post via email
def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            # ... send email
    else:
        form = EmailPostForm()
    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form
        }
    )


# View function for displaying a list of posts (with optional tag filtering)
def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Pagination with 10 posts per page
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range, get last page of results
        posts = paginator.page(paginator.num_pages)

    return render(
        request,
        'blog/post/list.html',
        {'posts': posts, 'tag': tag if tag_slug else None}
    )


# View function for displaying a single post detail page
def post_detail(request, year, month, day, post_slug):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post_slug,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )

    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for user to comment
    form = CommentForm()

    # Get IDs of tags associated with the current post
    post_tags_ids = post.tags.values_list('id', flat=True)

    # Step 1: Find posts that share at least one tag
    tag_based_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(id=post.id)

    # Step 2: Find posts with similar titles (using trigram similarity)
    # Only do this if we have fewer than 4 tag-based posts
    title_based_posts = Post.published.none()
    if tag_based_posts.count() < 4:
        title_based_posts = Post.published.annotate(
            similarity=TrigramSimilarity('title', post.title)
        ).filter(
            similarity__gt=0.1  # Threshold: 0.1 is lenient enough to match short words like "do"
        ).exclude(id=post.id).order_by('-similarity')[:4 - tag_based_posts.count()]

    # Combine both sets of posts and remove duplicates
    similar_posts = (tag_based_posts | title_based_posts).distinct()

    # Annotate with tag count and sort
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags', '-publish')[:4]

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

# View function for handling comment submission (POST only)
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )

# View function for searching posts by keyword
def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # 1. Full-text search on title and body (with weights)
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)

            full_text_results = Post.published.annotate(
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.1).order_by('-rank', '-publish')

            # 2. Trigram similarity search on title and body
            trigram_results = Post.published.annotate(
                title_similarity=TrigramSimilarity('title', query),
                body_similarity=TrigramSimilarity('body', query),
                total_similarity=(
                    TrigramSimilarity('title', query) * 2 +
                    TrigramSimilarity('body', query)
                )
            ).filter(
                Q(title_similarity__gt=0.1) | Q(body_similarity__gt=0.1)
            ).order_by('-total_similarity', '-publish')

            # 3. Combine both result sets and remove duplicates
            combined_results = (full_text_results | trigram_results).distinct()

            # 4. Final ranking: prioritize full-text results, then trigram similarity
            results = combined_results.annotate(
                final_rank=SearchRank(search_vector, search_query) + (TrigramSimilarity('title', query) * 2)
            ).order_by('-final_rank', '-publish')

    return render(
        request,
        'blog/post/search.html',
        {
            'form': form,
            'query': query,
            'results': results
        }
    )