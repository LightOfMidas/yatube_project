from django.shortcuts import get_object_or_404, render
from .models import Group, Post


def index(request):
    posts = Post.objects.order_by('-pub_date')[:10]
    title = 'Это главная страница проекта Yatube'
    context = {
        'title': title,
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group_list_title = 'Здесь будет информация о группах проекта Yatube'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        'group_list_title': group_list_title,
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)
