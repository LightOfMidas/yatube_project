from django import forms
from django.forms import ModelForm

from .models import Post, User


class PostForm(ModelForm):
    author = forms.ModelChoiceField(queryset=User.objects.all(),
                                    widget=forms.widgets.HiddenInput)

    class Meta:
        model = Post
        fields = ('text', 'group', 'author')
        labels = {
            'group': ('Группа'),
            'text': ('Текст'),
            'author': ('Автор'),
        }
