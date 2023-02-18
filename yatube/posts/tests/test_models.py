from django.test import TestCase
from mixer.backend.django import mixer

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post)

    def test_postmodel_have_correct_len_str(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = self.post
        text = post.text[:15]
        self.assertEqual(text, str(post))

    def test_verbose_names(self):
        """Проверяем, что название полей соответсвует ожидаемому"""
        post = self.post
        field_verbose = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_texts(self):
        """Проверка наличия текста помощи"""
        post = self.post
        field_help_text = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend(Group)

    def test_model_group_title(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = self.group
        title = group.title
        self.assertEqual(title, str(group))
