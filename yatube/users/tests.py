from django.test import TestCase
from django.urls import reverse

from posts.models import User


class UsersPostTest(TestCase):
    """
    Тест кейс форм приложения users
    """

    def test_form_data_valid_signup(self):
        """
        Проверка создания пользователя при валидном заполнении формы
        """
        response = self.client.post(
            reverse('users:signup'),
            data={
                'first_name': 'Aleksey',
                'last_name': 'Sosov',
                'username': 'TestUser',
                'email': 'test@mail.ru',
                'password1': '1234567Aa',
                'password2': '1234567Aa',
            }
        )
        self.assertEqual(
            1,
            User.objects.count(),
            msg='Пользователь не создался - ошибки заполнения формы'
        )
        self.assertRedirects(response, reverse(
            'posts:index'),
            msg_prefix='Неверная переадресация после создания пользователя'
        )
