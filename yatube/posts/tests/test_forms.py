import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from http import HTTPStatus

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test-user')
        cls.group = Group.objects.create(
            title='title',
            slug='test-slug',
        )
        cls.other_group = Group.objects.create(
            title='other-title',
            slug='other-test-slug',
        )
        cls.post = Post.objects.create(
            text='texts',
            author=cls.user,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        cache.clear()

    def test_authorized_user_create_post(self):
        """Проверка валидации и создания новой записи Post"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertRedirects(response, reverse('posts:profile',
                                               args=(self.user.username,)))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text='text',
            ).exists()
        )
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.text, 'text')

    def test_not_authorized_user_create_post(self):
        """Проверка работы create_post для не авторизированного пользователя"""
        post_count = Post.objects.count()
        response = self.client.get(reverse('posts:post_create'))
        login = reverse('users:login')
        post_create = reverse('posts:post_create')
        self.assertRedirects(response, f"{login}?next={post_create}")
        self.assertEqual(Post.objects.count(), post_count)

    def test_edit_post(self):
        """Проверка работы edit_post"""

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'new-text',
            'group': self.other_group.id,
            'image': uploaded
        }
        response = self.authorized_user.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(self.post.id,)))
        self.assertTrue(
            Post.objects.filter(
                group=self.other_group.id,
                text='new-text',
                image='posts/small.gif'
            ).exists()
        )
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, 'new-text')
        self.assertEqual(post.group, self.other_group)
        response = self.authorized_user.get(reverse(
            'posts:group_list', args=(self.group.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context['page_obj']), 0)
