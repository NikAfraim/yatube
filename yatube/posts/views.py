from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .models import Follow, Group, Post, User
from .forms import CommentForm, PostForm
from .utils import paginator


def index(request):
    post_list = Post.objects.select_related('group', 'author').all()
    return render(request, 'posts/index.html',
                  {'page_obj': paginator(request, post_list)})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').all()
    return render(request, 'posts/group_list.html',
                  {'page_obj': paginator(request, post_list), 'group': group})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group').all()
    following = request.user.is_authenticated and author.following.filter(
        user=request.user).exists()
    count_follower = Follow.objects.filter(author=author).count()
    count_following = Follow.objects.filter(user=author).count()
    return render(request, 'posts/profile.html',
                  {'page_obj': paginator(request, post_list),
                   'count_post': len(post_list),
                   'author': author,
                   'following': following,
                   'count_follower': count_follower,
                   'count_following': count_following})


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.prefetch_related('comments__author'),
                             id=post_id)
    form = CommentForm(request.POST or None)
    return render(request, 'posts/post_detail.html',
                  {'post': post,
                   'form': form,
                   'comments': post.comments.all()})


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', {'form': form})


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
    posts_follow = Post.objects.filter(
        author__following__user=request.user).select_related('author', 'group')
    return render(request, 'posts/follow_index.html',
                  {'page_obj': paginator(request, posts_follow)})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(author__username=username,
                          user=request.user).delete()
    return redirect('posts:profile', username=username)
