from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from yatube.settings import POSTS_COUNT

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    posts = Post.objects.all()[:POSTS_COUNT]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    title = 'Это главная страница проекта Yatube'
    context = {
        'title': title,
        'posts': posts,
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group_list_title = 'Здесь будет информация о группах проекта Yatube'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:POSTS_COUNT]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        'group_list_title': group_list_title,
        'group': group,
        'posts': posts,
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=profile).all()[:POSTS_COUNT]
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    posts_count = post_list.count()
    page = paginator.get_page(page_number)
    context = {
        "profile": profile,
        "paginator": paginator,
        "posts_count": posts_count,
        "page": page,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_list = Post.objects.filter(author=profile).all()[:POSTS_COUNT]
    posts_count = post_list.count()
    context = {
        "post": post,
        "posts_count": posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['author'].username
            return redirect(reverse_lazy('posts:profile',
                                         kwargs={'username': username}))
        else:
            return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm(initial={'author': request.user})
    return render(request, 'posts/create_post.html', {'form': form})
