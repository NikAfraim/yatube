from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author')
        cls.user_follower = User.objects.create(username='follower')
        cls.other_user = User.objects.create(username='non_author')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )

    def setUp(self):
        """Создание пользователей"""
        self.author = Client()
        self.author.force_login(self.user)
        self.non_author = Client()
        self.non_author.force_login(self.other_user)
        self.follower = Client()
        self.follower.force_login(self.user_follower)
        self.urls = (
            ('posts:index', None,
             '/'),
            ('posts:group_list', (self.group.slug,),
             f'/group/{self.group.slug}/'),
            ('posts:profile', (self.user,),
             f'/profile/{self.user}/'),
            ('posts:post_detail', (self.post.id,),
             f'/posts/{self.post.id}/'),
            ('posts:post_create', None,
             '/create/'),
            ('posts:post_edit', (self.post.id,),
             f'/posts/{self.post.id}/edit/'),
            ('posts:add_comment', (self.post.id,),
             f'/posts/{self.post.id}/comment/'),
            ('posts:follow_index', None, '/follow/'),
            ('posts:profile_follow', (self.user,),
             f'/profile/{self.user.username}/follow/'),
            ('posts:profile_unfollow', (self.user_follower,),
             f'/profile/{self.user_follower}/unfollow/')

        )
        cache.clear()

    def test_templates_for_author(self):
        """Проверка шаблонов"""
        templates = (
            ('posts:index', None, 'posts/index.html',),
            ('posts:group_list', (self.group.slug,), 'posts/group_list.html',),
            ('posts:profile', (self.user,), 'posts/profile.html',),
            ('posts:post_detail', (self.post.id,), 'posts/post_detail.html',),
            ('posts:post_create', None, 'posts/create_post.html',),
            ('posts:post_edit', (self.post.id,), 'posts/create_post.html'),
            ('posts:follow_index', None, 'posts/follow_index.html')
        )
        for url, arg, template in templates:
            with self.subTest(url=url):
                response = self.author.get(reverse(url, args=arg))
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_author(self):
        """Проверка доступа для автора"""
        for url, arg, hardcode in self.urls:
            with self.subTest(url=url):
                response = self.author.get(reverse(url, args=arg))
                if url == 'posts:add_comment':
                    self.assertRedirects(response, reverse('posts:post_detail',
                                                           args=arg))
                elif url in ['posts:profile_follow', 'posts:profile_unfollow']:
                    self.assertRedirects(response, reverse('posts:profile',
                                                           args=arg))
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_non_author(self):
        """Проверка доступа для не автора"""
        for url, arg, hardcode in self.urls:
            with self.subTest(url=url):
                response = self.non_author.get(reverse(url, args=arg),
                                               follow=True)
                if url in ['posts:post_edit', 'posts:add_comment']:
                    self.assertRedirects(response, reverse(
                        'posts:post_detail', args=arg))
                elif url in ['posts:profile_follow', 'posts:profile_unfollow']:
                    self.assertRedirects(response, reverse('posts:profile',
                                                           args=arg))
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_non_authorized(self):
        """Проверка доступа для не авторизированного пользователя"""
        for url, arg, hardcode in self.urls:
            with self.subTest(url=url):
                response = self.client.get(reverse(url, args=arg))
                login = reverse('users:login')
                if url in ['posts:post_edit', 'posts:post_create',
                           'posts:add_comment', 'posts:follow_index',
                           'posts:profile_follow', 'posts:profile_unfollow']:
                    unique_reverse = reverse(url, args=arg)
                    self.assertRedirects(response,
                                         f'{login}?next={unique_reverse}')
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_reverse(self):
        """Проверка reverse"""
        for url, arg, hardcode in self.urls:
            with self.subTest(url=url):
                self.assertEqual(reverse(url, args=arg), hardcode)
