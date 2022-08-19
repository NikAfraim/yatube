from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()

# -*-coding:utf-8-*-


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост  ',
        )
        cache.clear()

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = self.group
        post = self.post
        field = {
            group.title: group,
            post.text[:15]: post,
        }
        for obj, obj_str in field.items():
            with self.subTest(str=obj):
                self.assertEqual(obj, str(obj_str))

    def test_help_text(self):
        """Проверка, что help_text совпадает с ожидаемым."""
        post = self.post
        help_text_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text_text,
                         'Прошу, пиши, что хочешь, свобода действий')
        hel_text_group = post._meta.get_field('group').help_text
        self.assertEqual(hel_text_group, 'Ну выбери уже')

    def test_verbose(self):
        """Проверка, что verbose совпадает с ожидаемым."""
        post = self.post
        verbose_text = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose_text, 'текст')
        verbose_author = post._meta.get_field('author').verbose_name
        self.assertEqual(verbose_author, 'автор')
        verbose_pub_date = post._meta.get_field('pub_date').verbose_name
        self.assertEqual(verbose_pub_date, 'дата публикации')
        verbose_group = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose_group, 'сообщество')
