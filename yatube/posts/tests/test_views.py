import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Post, Group, Follow
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'testslug'
GROUP_DESCRIPTION = 'Тестовое описание'
POST_TEXT = 'Тестовый пост'
small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')
UPLOADED = SimpleUploadedFile(name='small.gif',
                              content=small_gif,
                              content_type='image/gif')

GROUP_TITLE2 = 'Тестовая группа2'
GROUP_SLUG2 = 'testslug2'
GROUP_DESCRIPTION2 = 'Тестовое описание2'

COUNT_POST_FIRST = 10
COUNT_POST_SECOND = 3


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )

        cls.group2 = Group.objects.create(
            title=GROUP_TITLE2,
            slug=GROUP_SLUG2,
            description=GROUP_DESCRIPTION2,
        )

        cls.user_author = User.objects.create_user(username="user_author")
        cls.another_user = User.objects.create_user(username="another_user")

        cls.post = Post.objects.create(
            author=cls.user_author,
            text=POST_TEXT,
            group=cls.group,
            image=UPLOADED,
        )

        cls.follow = Follow.objects.create(
            user=cls.another_user,
            author=cls.user_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.unauthorized_user = Client()
        self.post_author = Client()
        self.post_author.force_login(self.user_author)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.another_user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
            'posts/post_detail.html',
            reverse('posts:allrecord', kwargs={'slug': GROUP_SLUG}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'user_author'}):
            'posts/profile.html'}
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_for_post_author_correct_template(self):
        """URL-адрес использует шаблон posts/create_post.html."""
        response = self.post_author.get(reverse('posts:post_edit',
                                                kwargs={'post_id': '1'}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_title_0 = first_object.group.title
        self.assertEqual(post_title_0, GROUP_TITLE)

        post_text_0 = first_object.text
        self.assertEqual(post_text_0, POST_TEXT)

        post_slug_0 = first_object.group.slug
        self.assertEqual(post_slug_0, GROUP_SLUG)

        post_image_0 = first_object.image
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse('posts:allrecord',
                                            kwargs={'slug': GROUP_SLUG}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, POST_TEXT)

        post_group_0 = first_object.group.title
        self.assertEqual(post_group_0, GROUP_TITLE)

        post_description_0 = first_object.group.description
        self.assertEqual(post_description_0, GROUP_DESCRIPTION)

        post_image_0 = first_object.image
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_notexists_group_page(self):
        """"Страница группы testslug2 не содержит посты группы testslug"""
        response = self.authorized_user.get("/group/testslug2/")
        self.assertNotIn(Post.objects.get(id=1), response.context['page_obj'])

    def test_create_post_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse('posts:post_create'))
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse('posts:profile',
                                            kwargs={'username': 'user_author'})
                                            )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_description_0 = first_object.group.description
        self.assertEqual(post_text_0, POST_TEXT)
        self.assertEqual(post_group_0, GROUP_TITLE)
        self.assertEqual(post_description_0, GROUP_DESCRIPTION)

        second_object = response.context['posts'][0]
        post_text_1 = second_object.text
        post_group_1 = first_object.group.title
        post_description_1 = first_object.group.description
        self.assertEqual(post_text_1, POST_TEXT)
        self.assertEqual(post_group_1, GROUP_TITLE)
        self.assertEqual(post_description_1, GROUP_DESCRIPTION)

        third_object = response.context['author']
        post_author = third_object.username
        self.assertEqual(post_author, 'user_author')

        post_image_0 = first_object.image
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse('posts:post_detail',
                                            kwargs={'post_id': '1'})
                                            )
        first_object = response.context['post']
        post_text = first_object.text
        post_group = first_object.group.title
        post_description = first_object.group.description
        self.assertEqual(post_text, POST_TEXT)
        self.assertEqual(post_group, GROUP_TITLE)
        self.assertEqual(post_description, GROUP_DESCRIPTION)
        response = self.authorized_user.get(reverse('posts:post_detail',
                                                    kwargs={'post_id': '1'})
                                            )

        second_object = response.context['posts'][0]
        posts_text = second_object.text
        posts_group = second_object.group.title
        posts_description = second_object.group.description
        self.assertEqual(posts_text, POST_TEXT)
        self.assertEqual(posts_group, GROUP_TITLE)
        self.assertEqual(posts_description, GROUP_DESCRIPTION)

        post_image_0 = first_object.image
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse('posts:post_edit',
                                            kwargs={'post_id': '1'})
                                            )
        first_object = response.context['post']
        post_text = first_object.text
        post_group = first_object.group.title
        post_description = first_object.group.description
        self.assertEqual(post_text, POST_TEXT)
        self.assertEqual(post_group, GROUP_TITLE)
        self.assertEqual(post_description, GROUP_DESCRIPTION)

    def test_follow_page_show_correct_context(self):
        """Шаблон follow сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse('posts:follow_index'))
        first_object = response.context['post']
        post_text = first_object.text
        post_group = first_object.group.title
        post_description = first_object.group.description
        self.assertEqual(post_text, POST_TEXT)
        self.assertEqual(post_group, GROUP_TITLE)
        self.assertEqual(post_description, GROUP_DESCRIPTION)

    def test_cache_index_page_correct_context(self):
        """Кэш index сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse('posts:index'))
        context = response.context['page_obj'][0]
        content = response.content

        post_title_0 = context.group.title
        self.assertEqual(post_title_0, GROUP_TITLE)

        post_text_0 = context.text
        self.assertEqual(post_text_0, POST_TEXT)

        post_slug_0 = context.group.slug
        self.assertEqual(post_slug_0, GROUP_SLUG)

        post_image_0 = context.image
        self.assertEqual(post_image_0, 'posts/small.gif')

        post_id = PostsPagesTests.post.id
        instance = Post.objects.get(pk=post_id)
        instance.delete()

        new_response = self.authorized_user.get(reverse('posts:index'))
        new_content = new_response.content
        self.assertEqual(content, new_content)

        cache.clear()
        new_new_response = self.authorized_user.get(reverse('posts:index'))
        new_new_content = new_new_response.content
        self.assertNotEqual(content, new_new_content)


object_list = []


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user_author')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=POST_TEXT,
                group=cls.group,
            )
            object_list.append(cls.post)

    def test_index_first_page_contains_ten_records(self):
        """Количество постов на первой странице равно 10."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), COUNT_POST_FIRST)

    def test_index_second_page_contains_three_records(self):
        """Количество постов на второй странице равно 3."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), COUNT_POST_SECOND)

    def test_group_list_first_page_contains_ten_records(self):
        """Количество постов на первой странице равно 10."""
        response = self.client.get(reverse(
            'posts:allrecord', kwargs={'slug': GROUP_SLUG}))
        self.assertEqual(len(response.context['page_obj']), COUNT_POST_FIRST)

    def test_group_list_second_page_contains_three_records(self):
        """Количество постов на второй странице равно 3."""
        response = self.client.get(reverse(
            'posts:allrecord', kwargs={'slug': GROUP_SLUG}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), COUNT_POST_SECOND)

    def test_profile_list_first_page_contains_ten_records(self):
        """Количество постов на первой странице равно 10."""
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': 'user_author'}))
        self.assertEqual(len(response.context['page_obj']), COUNT_POST_FIRST)

    def test_profile_list_second_page_contains_three_records(self):
        """Количество постов на второй странице равно 3."""
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': 'user_author'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), COUNT_POST_SECOND)
