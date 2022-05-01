from .models import Post, User
from django import forms
from django.forms import ModelForm


class PostForm(ModelForm):
    author = forms.ModelChoiceField(queryset=User.objects.all(),
                                    widget=forms.widgets.HiddenInput)

    class Meta:
        model = Post
        fields = ('text', 'group', 'author')
