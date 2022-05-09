from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_COUNT

from .forms import PostForm
from .models import Group, Post, User

User = get_user_model()


def index(request):
    posts = Post.objects.all()[:POSTS_COUNT]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Это главная страница проекта Yatube'
    context = {
        'title': title,
        'posts': posts,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group_list_title = 'Здесь будет информация о группах проекта Yatube'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:POSTS_COUNT]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group_list_title': group_list_title,
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile).all()[:POSTS_COUNT]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts_count = posts.count()
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'paginator': paginator,
        'posts_count': posts_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    posts = Post.objects.filter(author=profile).all()[:POSTS_COUNT]
    posts_count = posts.count()
    context = {
        'profile': profile,
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    title = 'Добавить запись'
    btn_caption = 'Добавить'
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile')
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
    if post.author != user:
        return redirect('posts:post_detail',
                        username=user.username, post_id=post_id)
    title = 'Редактировать запись'
    btn_caption = 'Сохранить'
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('posts:post_detail', username=request.user.username,
                        post_id=post_id)
    context = {
        'form': form,
        'title': title,
        'btn_caption': btn_caption,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)
