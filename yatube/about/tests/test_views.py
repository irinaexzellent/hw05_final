from django.test import Client, TestCase
from django.urls import reverse


class AboutPagesTests(TestCase):

    def setUp(self):
        self.unauthorized_user = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'}
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.unauthorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)
