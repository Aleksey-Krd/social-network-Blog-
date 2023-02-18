from http import HTTPStatus

from django.test import TestCase, Client


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exists_at_desired_location(self):
        """Проверка доступности адресов приложения about"""
        urls_list = [
            '/about/author/',
            '/about/tech/',
        ]
        for url in urls_list:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """Проверка шаблонов приложения about"""
        template_list = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in template_list.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
