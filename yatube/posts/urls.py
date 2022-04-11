from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('groups', views.groups),
    path('groups/group/<slug:slug>', views.group_posts())
]
