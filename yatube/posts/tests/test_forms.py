import shutil
import tempfile

from posts.forms import PostForm, CommentForm
from posts.models import Post, Group
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

import datetime
from django.utils import timezone

from django.contrib.auth import get_user_model

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'testslug'
GROUP_DESCRIPTION = 'Тестовое описание'
POST_TEXT = 'Тестовый пост'
POST_COMMENT = 'Тестовый комментарий'
POST_DATE = datetime.datetime.strptime("2022-01-01 22:24:00",
                                       "%Y-%m-%d %H:%M:%S")
CTZ = timezone.get_current_timezone()
t1 = CTZ.localize(POST_DATE)

POST_TEXT_EDIT = 'Тестовый пост заменен'
POST_DATE_EDIT = datetime.datetime.strptime("2022-02-16 22:24:00",
                                            "%Y-%m-%d %H:%M:%S")
current_tz = timezone.get_current_timezone()
t2 = CTZ.localize(POST_DATE_EDIT)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.another_user = User.objects.create_user(username="another_user")
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
            pub_date=t1,
        )

        cls.form = PostForm()

    def setUp(self):
        self.post_author = Client()
        self.post_author.force_login(self.user)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.another_user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        author = PostCreateFormTests.user
        group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='testslug2',
            description='Тестовое описание2',
        )

        form_data = {
            'author': author,
            'text': 'Тестовый пост 2',
            'pub_date': '01-01-2020',
            'group': group2.id,
            'image': uploaded,
        }
        response = self.post_author.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'testuser'}))

        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(
            Post.objects.filter(text='Тестовый пост 2',
                                group=group2.id,
                                image='posts/small.gif').exists())
        post2 = Post.objects.get(id=2)
        self.assertTrue(post2)

    def test_post_edit_post(self):
        """Валидная форма заменяет запись в Post."""
        posts_count = Post.objects.count()
        author = PostCreateFormTests.user
        group3 = Group.objects.create(
            title='Тестовая группа3',
            slug='testslug3',
            description='Тестовое описание3',
        )

        form_data = {
            'author': author,
            'text': POST_TEXT_EDIT,
            'pub_date': t2,
            'group': group3.id
        }
        response = self.post_author.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data
        )

        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': '1'}))
        self.assertTrue(
            Post.objects.filter(text=POST_TEXT_EDIT,
                                group=group3.id).exists())
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_1_exists(self):
        """Проверка наличия поста с id=1."""
        post1 = Post.objects.get(id=1)
        self.assertTrue(post1)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
            pub_date=t1,
        )
        cls.form = CommentForm()

    def setUp(self):
        self.post_author = Client()
        self.post_author.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_comment_create_post(self):
        """Валидная форма создает комментарий для поста."""
        comment = CommentCreateFormTests.user
        form_data = {'text': comment}
        response = self.post_author.post(
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            data=form_data)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'}))
