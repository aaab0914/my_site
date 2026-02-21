from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage,  PageNotAnInteger
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.postgres.search import(
    SearchVector,
    SearchQuery,
    SearchRank,
)
from taggit.models import Tag

from .models import Post
from .forms import EmailPostForm, CommentForm, SearchForm
# from django.contrib.postgres.


class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 10
    template_name = 'blog/post/list.html'

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

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tags = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Pagination with 10 post per page
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page', 1)
    try:
        posts= paginator.page(page_number)
    except PageNotAnInteger:  # ⬅️ 添加这个异常处理
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range get last page of results.
        posts = paginator.page(paginator.num_pages)
    # posts = paginator.page(page_number)

    return render(
        request,
        'blog/post/list.html',
        {'posts': posts}
    )

def post_detail(request, year, month, day, post_slug):
    post = get_object_or_404(
        Post,
        # id=id,
        status=Post.Status.PUBLISHED,
        slug=post_slug,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )

    # List of active comment for this post
    comments = post.comments.filter(active=True)
    # Form for user to comment
    form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags', '-publish')[:4]

    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("No Post found.")
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
        # Assign the past to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'for,': form,
            'comment': comment
        }
    )


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title',
                                         weight='A')+ SearchVector('body',
                                                                   weight='B')
            search_query = SearchQuery(query)

            results = Post.published.annotate(
                similarity=TrigramSimilarity(
                    'title',
                    query
                ),
                # search=search_vector,
                # rank=SearchRank(search_vector, search_query)
            ).filter(similarity__gt=0.1).order_by('-similarity')

    return render(
        request,
        'blog/post/search.html',
        {
            'form': form,
            'query': query,
            'results': results
        }
    )