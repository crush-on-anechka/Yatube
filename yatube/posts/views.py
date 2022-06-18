from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .paginator import paginator
from django.views.decorators.cache import cache_page


@cache_page(20, key_prefix='index_page')
def index(request):
    posts = Post.objects.select_related('author', 'group')
    context = {
        'page_obj': paginator(request, posts)
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author', 'group')
    context = {
        'group': group,
        'page_obj': paginator(request, posts)
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author', 'group')
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        )
    context = {
        'author': author,
        'posts_count': posts.count(),
        'following': following,
        'my_page': request.user != author,
        'page_obj': paginator(request, posts)
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    form = CommentForm(
        request.POST or None,
        files=request.FILES or None
    )
    post = get_object_or_404(Post, id=post_id)
    posts = post.author.posts.select_related('author', 'group')
    comments = post.comments.select_related('author', 'post')
    edit_visible = False
    if post.author == request.user:
        edit_visible = True
    context = {
        'post': post,
        'posts_count': posts.count(),
        'edit_visible': edit_visible,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if not request.method == 'POST' or not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    model_instance = form.save(commit=False)
    model_instance.author = request.user
    model_instance.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    user = get_object_or_404(User, username=request.user)
    posts = Post.objects.filter(author__following__user=user)
    context = {
        'page_obj': paginator(request, posts)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=request.user)
    if not Follow.objects.filter(user=user, author=author) and author != user:
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=request.user)
    Follow.objects.filter(
        author=author,
        user=user
    ).delete()
    return redirect('posts:profile', username)
