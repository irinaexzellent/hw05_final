from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_author = User.objects.create_user(username="user_author")
        cls.another_user = User.objects.create_user(username="another_user")

    def setUp(self):
        self.unauthorized_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user_author)

    def test_sighup(self):
        response = self.unauthorized_user.get('/signup/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_logout(self):
        response = self.unauthorized_user.get('/logout/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_login(self):
        response = self.unauthorized_user.get('/login/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_users_correct_template_unauthorized_user(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:login'): 'users/login.html'}
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.unauthorized_user.get(address)
                self.assertTemplateUsed(response, template)
