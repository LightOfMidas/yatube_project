from core.utils import paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    posts = Post.objects.all()
    page_obj = paginator(request, posts)
    title = 'Это главная страница проекта Yatube'
    context = {
        'title': title,
        'page_obj': page_obj,
        'is_index': True
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group_list_title = 'Здесь будет информация о группах проекта Yatube'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator(request, posts)
    context = {
        'group_list_title': group_list_title,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).all()
    posts_count = posts.count()
    page_obj = paginator(request, posts)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    profile = author
    context = {
        'profile': profile,
        'posts_count': posts_count,
        'page_obj': page_obj,
        'following': following,
        'profile': profile
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'comments': post_comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    title = 'Добавить запись'
    btn_caption = 'Добавить'
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    context = {
        'form': form,
        'title': title,
        'btn_caption': btn_caption,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    author = post.author
    title = 'Сохранить запись'
    btn_caption = 'Сохранить'
    if author != user:
        return redirect('posts:profile', request.user)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect(reverse_lazy('posts:post_detail',
                                     kwargs={'post_id': post_id}))
    context = {
        'is_edit': True,
        'form': form,
        'post_id': post_id,
        'title': title,
        'btn_caption': btn_caption,
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
    return redirect(reverse(
        'posts:post_detail',
        kwargs={
            'post_id': post_id}))


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, posts)
    title = 'Подписки'
    context = {
        'page_obj': page_obj,
        'title': title,
        'is_follow': True
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    profile = get_object_or_404(User, username=username)
    current_user = request.user
    if current_user != profile:
        Follow.objects.get_or_create(
            user=request.user,
            author=profile
        )
    return redirect(reverse('posts:profile', kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    profile = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=profile).delete()
    return redirect(reverse('posts:profile', kwargs={'username': username}))
