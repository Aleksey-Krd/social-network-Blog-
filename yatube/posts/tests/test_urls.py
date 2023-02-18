from http import HTTPStatus

from django.test import TestCase, Client
from mixer.backend.django import mixer

from posts.models import Post, Group, User
from posts import constants as c


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            text='123',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(self.user)

    def test_url_correction(self):
        """
        Проверяем доступность страниц неавторизованному пользователю
        """
        data_url_list = [
            ('/', HTTPStatus.OK, False),
            (f'/group/{self.group.slug}/', HTTPStatus.OK, False),
            (f'/group/{self.group.slug}/', HTTPStatus.OK, False),
            (f'/profile/{self.user}/', HTTPStatus.OK, False),
            (f'/posts/{self.post.id}/', HTTPStatus.OK, False),
            (f'/posts/{self.post.id}/edit/', HTTPStatus.OK, True),
            ('/create/', HTTPStatus.OK, True),
            ('/unexisting_page/', HTTPStatus.NOT_FOUND, False)
        ]
        for url, status, auth_ok in data_url_list:
            with self.subTest(url=url):
                if auth_ok:
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                    response_auth = self.auth.get(url)
                    self.assertEqual(response_auth.status_code, status)
                else:
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_templates_correction(self):
        """
        Проверяем правильность использования шаблонов
        """
        templates_list = {
            c.TEMPLATE_INDEX: '/',
            c.TEMPLATE_GROUP_POSTS: f'/group/{self.group.slug}/',
            c.TEMPLATE_PROFILE: f'/profile/{self.user}/',
            c.TEMPLATE_POST_ID: f'/posts/{self.post.id}/',
            c.TEMPLATE_EDIT: f'/posts/{self.post.id}/edit/',
            c.TEMPLATE_CREATE: '/create/',
        }

        for template, address in templates_list.items():
            with self.subTest(address=address):
                response = self.auth.get(address)
                self.assertTemplateUsed(response, template)
