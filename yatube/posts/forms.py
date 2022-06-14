from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'group': ('Группа'),
            'text': ('Текст'),
            'image': ('Изображение')
        }
        help_texts = {
            'group': 'Выберите группу',
            'text': 'Введите текст',
            'image': 'Загрузите изображение'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        label = {
            'text': ('Комментарий')
        }
        help_texts = {
            'text': 'Введите комментарий'
        }
