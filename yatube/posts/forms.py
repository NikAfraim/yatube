from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {'text': 'Введите текст',
                  'group': 'Выберите группу',
                  'image': 'Загрузить картинку'}
        help_texts = {'text': 'Введите, что в голову придет',
                      'group': 'Ну выбери уже',
                      'image': 'Хотите вставить картинку? Прошу!'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = {'text', }
        labels = {'text': 'Введите текст'}
        help_texts = {'text': 'Введите, что в голову придет'}

