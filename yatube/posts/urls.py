from django.urls import path

from . import views

app_name = 'yatube'

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>', views.group_posts, name='group_list')
]
