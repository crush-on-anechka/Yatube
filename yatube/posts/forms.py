from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    button_save = 'Сохранить'
    button_add = 'Добавить'

    class Meta:
        model = Post
        fields = [
            'text',
            'group',
            'image'
        ]
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Картинка'
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Загруженная картинка'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Текст поста'}
        help_texts = {'text': 'Текст нового поста'}
