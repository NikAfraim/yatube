from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django import forms

from ..models import Comment, Follow, Group, Post
from ..forms import PostForm
from django.conf import settings

User = get_user_model()
COUNT_OF_POST = 13
NUMBER_OF_POSTS_IN_OTHER_GROUP_LIST = 0
LIST_OF_POSTS_BY_UNFOLLOWER = []
ZERO_FOLLOWER = 0


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create(username='user')
        cls.other_user = User.objects.create(username='other_user')
        cls.group = Group.objects.create(title='Заголовок', slug='test-slug',
                                         description='text')
        cls.other_group = Group.objects.create(title='Заголовок',
                                               slug='other-test-slug',
                                               description='text')
        cls.post = Post.objects.create(text='Текст', author=cls.user,
                                       group=cls.group, image=cls.uploaded)
        cls.comment = Comment.objects.create(
            text='comment',
            post=cls.post,
            author=cls.user
        )

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.user_check_follow = Client()
        self.user_check_follow.force_login(self.other_user)
        cache.clear()

    def context(self, response, value=False):
        if value:
            context_of_object = response.context['post']
        else:
            context_of_object = response.context['page_obj'][0]
        self.assertEqual(context_of_object.author, self.post.author)
        self.assertEqual(context_of_object.text, self.post.text)
        self.assertEqual(context_of_object.group, self.post.group)
        self.assertEqual(context_of_object.pub_date,
                         self.post.pub_date)
        self.assertEqual(context_of_object.image, self.post.image)
        self.assertContains(response, '<img')

    def test_index_show_correct_context(self):
        """Проверка на корректность context для index"""
        response = self.authorized_user.get(reverse('posts:index'))
        self.context(response)

    def test_group_list_show_correct_context(self):
        """Проверка на корректность context для group_list"""
        response = self.authorized_user.get(reverse(
            'posts:group_list', args=(self.group.slug,)))
        self.context(response)
        self.assertEqual(response.context['group'], self.group)

    def test_group_list_without_posts(self):
        """Проверка на корректность context для group_list без постов"""
        new_post = Post.objects.create(text='Новый текст',
                                       author=self.user,
                                       group=self.group)
        response = self.authorized_user.get(reverse(
            'posts:group_list', args=(self.other_group.slug,)))
        group_context = response.context['group']
        post_by_other_group = list(group_context.posts.all())
        self.assertNotEqual(NUMBER_OF_POSTS_IN_OTHER_GROUP_LIST,
                            post_by_other_group)
        self.assertEqual(new_post.group, self.group)
        response = self.authorized_user.get(reverse(
            'posts:group_list', args=(self.group.slug,)))
        new_post_in_posts = response.context['group'].posts.all()
        self.assertIn(new_post, new_post_in_posts)

    def test_profile_show_correct_context(self):
        """Проверка на корректность context для profile"""
        response = self.authorized_user.get(reverse(
            'posts:profile', args=(self.user,)))
        self.context(response)
        self.assertEqual(response.context['author'], self.user)

    def test_post_details_show_correct_context(self):
        """Проверка на корректность context для post_details"""
        response = self.authorized_user.get(reverse(
            'posts:post_detail', args=(self.post.id,)))
        self.context(response, True)

    def test_forms(self):
        """Проверка форм post_create и post_edit"""
        urls = (
            ('posts:post_edit', (self.post.id,)),
            ('posts:post_create', None)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for url, arg in urls:
            with self.subTest(url=url):
                response = self.authorized_user.get(reverse(url, args=arg))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            'form').fields.get(value)
                        self.assertIsInstance(form_field, expected)

    def test_commenting_only_for_authorized_users(self):
        """Проверка, что комментировать посты
         может только авторизированный пользователь"""
        count = Post.objects.count()
        response = self.client.get(reverse('posts:add_comment',
                                           args=(self.post.id,)))
        login = reverse('users:login')
        comment = reverse('posts:add_comment', args=(self.post.id,))
        self.assertRedirects(response, f'{login}?next={comment}')
        response = self.authorized_user.get(reverse('posts:add_comment',
                                            args=(self.post.id,)))
        self.assertRedirects(response, reverse('posts:post_detail',
                                               args=(self.post.id,)))
        self.assertEqual(count, Post.objects.count())

    def test_new_comment(self):
        """Проверка, что появляется новый комментарий на post_detail"""
        Comment.objects.all().delete()
        count = Comment.objects.count()
        Comment.objects.create(
            text='comment',
            post=self.post,
            author=self.user
        )
        response = self.authorized_user.get(reverse('posts:post_detail',
                                                    args=(self.post.id,)))
        self.assertIn('comments', response.context)
        comment_context = response.context['comments'][0]
        self.assertEqual(comment_context.text, self.comment.text)
        self.assertEqual(comment_context.post, self.comment.post)
        self.assertEqual(comment_context.author, self.comment.author)
        self.assertNotEqual(count, Comment.objects.count())

    def test_cache(self):
        """Проверка работы кэша"""
        Post.objects.all().delete()
        Post.objects.create(
            text='Текст', author=self.user,
            group=self.group, image=self.uploaded
        )
        response_first = self.authorized_user.get(reverse('posts:index'))
        Post.objects.all().delete()
        response_second = self.authorized_user.get(reverse('posts:index'))
        self.assertEquals(response_first.content, response_second.content)
        cache.clear()
        response_third = self.authorized_user.get(reverse('posts:index'))
        self.assertNotEquals(response_first.content, response_third.content)

    def test_follow_index(self):
        """Проверка, что новые записи пользователя,
        появляются в ленте у фоловера и
        не появляются у не фоловера"""
        Post.objects.all().delete()
        Post.objects.create(
            text='Текст',
            author=self.user,
        )
        response = self.user_check_follow.get(reverse(
            'posts:follow_index'))
        posts_by_unfollower = list(response.context['page_obj'])
        self.assertEqual(LIST_OF_POSTS_BY_UNFOLLOWER,
                         posts_by_unfollower)
        Follow.objects.create(author=self.user,
                              user=self.other_user)
        response = self.user_check_follow.get(reverse(
            'posts:follow_index'))
        posts_by_follower = list(response.context['page_obj'])
        self.assertNotEqual(LIST_OF_POSTS_BY_UNFOLLOWER,
                            posts_by_follower)

    def test_follow(self):
        """Проверка, что авторизированный пользователь,
         может подписываться"""
        self.assertEqual(ZERO_FOLLOWER, Follow.objects.count())
        self.user_check_follow.get(reverse(
            'posts:profile_follow', args=(self.user,)))
        self.assertNotEqual(ZERO_FOLLOWER, Follow.objects.count())
        follow = Follow.objects.first()
        self.assertEqual(follow.author, self.user)
        self.assertEqual(follow.user, self.other_user)

    def test_unfollow(self):
        """Проверка, что авторизированный пользователь, может отписываться"""
        self.assertEqual(ZERO_FOLLOWER, Follow.objects.count())
        Follow.objects.create(author=self.user,
                              user=self.other_user)
        self.user_check_follow.get(reverse(
            'posts:profile_unfollow', args=(self.user,)))
        self.assertEqual(ZERO_FOLLOWER, Follow.objects.count())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.follower = User.objects.create(username='follower')
        Follow.objects.create(author=cls.user, user=cls.follower)
        cls.group = Group.objects.create(title='Заголовок', slug='test-slug',
                                         description='text')
        for _ in range(COUNT_OF_POST):
            cls.post = Post.objects.create(text='Текст', author=cls.user,
                                           group=cls.group)

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.follower)
        cache.clear()

    def test_paginator(self):
        """Проверка paginator"""
        urls = (
            ('posts:index', None),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.user,)),
            ('posts:follow_index', None)
        )
        pages = (
            ('?page=1', settings.NUMBER_OF_POSTS),
            ('?page=2', COUNT_OF_POST - settings.NUMBER_OF_POSTS)
        )
        for url, arg in urls:
            with self.subTest(url=url):
                for page, number_of_posts in pages:
                    with self.subTest(page=page):
                        response = self.authorized_user.get(reverse(
                            url, args=arg) + page)
                        self.assertEqual(
                            len(response.context['page_obj']), number_of_posts)
