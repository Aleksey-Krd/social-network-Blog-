from django.test import TestCase, Client

from posts.models import User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(self.user)

    def test_templates_correction(self):
        """
        Проверяем правильность использования шаблона 404 приложения Core
        """
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
