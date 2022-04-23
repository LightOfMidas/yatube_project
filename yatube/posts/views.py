from django.shortcuts import get_object_or_404, render

from yatube.settings import POSTS_COUNT

from .models import Group, Post


def index(request):
    posts = Post.objects.all()[:POSTS_COUNT]
    title = 'Это главная страница проекта Yatube'
    context = {
        'title': title,
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group_list_title = 'Здесь будет информация о группах проекта Yatube'
    group = get_object_or_404(Group, slug=slug)
    posts = group.elposto.all()[:POSTS_COUNT]
    context = {
        'group_list_title': group_list_title,
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)
