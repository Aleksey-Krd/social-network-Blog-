from http import HTTPStatus
import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from posts.models import Post, Group, User
from posts import constants as c

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = mixer.blend(Group)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(self.user)

    def test_valid_data_form_post_create(self):
        """
        Проверка создания поста если форма валидна
        """
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
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.auth.post(reverse(
            c.URL_NAME_CREATE),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(get_object_or_404(Post, id=1).image)

    def test_valid_data_form_post_edit(self):
        """
        Проверка редактирования поста если форма валидна
        """
        self.auth.post(reverse(
            c.URL_NAME_CREATE),
            data={'text': '2', 'group': self.group.id},
            follow=True
        )
        self.auth.post(reverse(
            c.URL_NAME_POST_EDIT,
            kwargs={'post_id': 1}),
            data={'text': 'Поменяли пост', 'group': ''},
        )
        self.assertTrue(Post.objects.filter(
            text='Поменяли пост',
            group=None,
            author=self.user).exists(),
            msg='Данные поста не совпадают с измененным'
        )
