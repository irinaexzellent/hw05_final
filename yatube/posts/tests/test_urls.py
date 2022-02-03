from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Тестовое описание',
        )

        cls.user_author = User.objects.create_user(username="user_author")
        cls.another_user = User.objects.create_user(username="another_user")

        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.unauthorized_user = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user_author)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.another_user)

    def test_urls_uses_correct_template_unauthorized_user(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:allrecord',
                    kwargs={'slug': 'testslug'}): 'posts/group_list.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:profile',
                    kwargs={'username': 'user_author'}): 'posts/profile.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.unauthorized_user.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_authorized_user(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:profile',
                    kwargs={'username': 'another_user'}): 'posts/profile.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': '1'}): 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_user.get(address)
                self.assertTemplateUsed(response, template)

    def test_added_url_uses_correct_template_post_author(self):
        """Страница /posts/<int:post_id>/edit/ использует шаблон
        posts/create_post.html."""
        response = self.post_author.get('/posts/1/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_unauthorized_user(self):
        """Страница доступна для неавторизированного пользователя."""
        url_names = [
            reverse('posts:index'),
            reverse('posts:allrecord', kwargs={'slug': 'testslug'}),
            reverse('posts:post_detail', kwargs={'post_id': '1'}),
            reverse('posts:profile', kwargs={'username': 'user_author'}),
        ]

        for address in url_names:
            with self.subTest(address=address):
                response = self.unauthorized_user.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_user(self):
        """Страница доступна для авторизированного пользователя."""
        url_names = [reverse('posts:post_create')]
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_user.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_author(self):
        """Страница доступна для автора поста."""
        response = self.post_author.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """Страница недоступна."""
        response = self.unauthorized_user.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_comment_page_unauthorized_user(self):
        """Страница недоступна."""
        response = self.unauthorized_user.get('posts:add_comment',
                                              kwargs={'post_id': '1'})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_add_comment_sub_unsub_authorized_user(self):
        """Страница доступна для авторизированного пользователя."""
        url_names = [
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            reverse('posts:profile_follow',
                    kwargs={'username': 'user_author'}),
            reverse('posts:profile_unfollow',
                    kwargs={'username': 'user_author'})
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_user.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
