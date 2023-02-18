from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import get_page


def index(request):
    posts_list = Post.objects.select_related('author').all()
    page_obj = get_page(posts_list, request)
    context = {
        'page_obj': page_obj,
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_group_lists = group.posts_group.all()
    page_obj = get_page(post_group_lists, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_post_list = user.user.all()
    if request.user.is_authenticated:
        following = request.user.follower.filter(following=user).exists()
    else:
        following = False
    page_obj = get_page(user_post_list, request)
    context = {
        'page_obj': page_obj,
        'author': user,
        'user_post_list': user_post_list,
        'user': request.user,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    posts_count = post.author.user.all()
    context = {
        'post': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_update(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return render(request, 'posts/update_post_not_author.html')
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'posts/update_post.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(
            'posts:profile', request.user.username
        )
    context = {
        'form': form,
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
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """
    Страница подписок пользователя
    """
    posts = Post.objects.select_related('author', 'group').filter(
        author__following__follower=request.user
    )
    context = {
        'page_obj': get_page(posts, request),
    }
    if len(context['page_obj']) == 0:
        return render(request, 'posts/follow_not.html', context)
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    following = get_object_or_404(User, username=username)
    follower = request.user
    if follower != following and (
        not follower.follower.filter(following=following).exists()
    ):
        Follow.objects.get_or_create(follower=follower, following=following)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow,
        follower=request.user,
        following__username=username,
    ).delete()
    return redirect('posts:profile', username)
