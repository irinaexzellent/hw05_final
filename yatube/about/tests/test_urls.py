from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class AboutURLTests(TestCase):
    def setUp(self):
        self.unauthorized_user = Client()

    def test_author(self):
        response = self.unauthorized_user.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        response = self.unauthorized_user.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_users_correct_template_unauthorized_user(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'}
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.unauthorized_user.get(address)
                self.assertTemplateUsed(response, template)
