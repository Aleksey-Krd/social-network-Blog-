from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import get_object_or_404
from mixer.backend.django import mixer
from django.core.cache import cache

from posts.models import Post, Group, User, Comment, Follow
from posts import constants as c


class PostsTests(TestCase):
    """
    Тест кейс приложения Post
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.follow = User.objects.create_user(username='Follower')
        cls.un_follow = User.objects.create_user(username='unFollower')
        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пятнадцать символов текста наверное',
            group=cls.group,
            image='posts/test.jpg'
        )

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(self.user)
        self.follower = Client()
        self.follower.force_login(self.follow)
        self.unfollower = Client()
        self.unfollower.force_login(self.un_follow)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон.
        """
        templates_pages_names = {
            c.TEMPLATE_INDEX: reverse(
                c.URL_NAME_INDEX
            ),
            c.TEMPLATE_GROUP_POSTS: reverse(
                c.URL_NAME_SLUG,
                kwargs={'slug': f'{self.group.slug}'}
            ),
            c.TEMPLATE_PROFILE: reverse(
                c.URL_NAME_PROFILE,
                kwargs={'username': f'{self.user.username}'}
            ),
            c.TEMPLATE_POST_ID: reverse(
                c.URL_NAME_POST_ID,
                kwargs={'post_id': f'{self.post.id}'}
            ),
            c.TEMPLATE_CREATE: reverse(
                c.URL_NAME_CREATE
            ),
            c.TEMPLATE_EDIT: reverse(
                c.URL_NAME_POST_EDIT,
                kwargs={'post_id': f'{self.post.id}'}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    msg_prefix='Неверное использование шаблонов post'
                )

    def test_index_page_show_correct_context(self):
        """
        Шаблон index.html сформирован с правильным контекстом.
        """
        response = self.auth.get(reverse(c.URL_NAME_INDEX))
        first_object = response.context['page_obj'][0]
        context_0 = {
            self.post.author.username: first_object.author.username,
            self.post.pub_date: first_object.pub_date,
            self.post.text: first_object.text,
        }
        for value, exp in context_0.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    exp,
                    msg='Неверные данные в context главной страницы'
                )

    def test_group_posts_correct_context(self):
        """
        Шаблон group_list.html сформирован с правильным контекстом
        """
        response = self.auth.get(reverse(
            c.URL_NAME_SLUG,
            kwargs={'slug': self.group.slug})
        )
        data_group_tests = {
            response.context['group'].title: self.group.title,
            response.context['group'].description: self.group.description,
            response.context['group'].slug: self.group.slug,
        }
        for value, exp in data_group_tests.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    exp,
                    msg='Неверные данные группы в context group_list'
                )

        page_object = response.context['page_obj']
        for post in page_object:
            data_post_test = {
                post.text[:15]: self.post.text[:15],
                post.author.username: self.post.author.username,
                post.id: self.post.pk,
                post.pub_date: self.post.pub_date,
            }
            for value, exp in data_post_test.items():
                with self.subTest(value=value):
                    self.assertEqual(
                        value,
                        exp,
                        msg='Неверные данные поста в context group_list'
                    )

    def test_profile_correct_context(self):
        """
        Шаблон profile.html сформирован с правильным контекстом
        """
        response = self.auth.get(reverse(
            c.URL_NAME_PROFILE,
            kwargs={'username': self.post.author.username})
        )

        page_objects = response.context['page_obj']
        for post in page_objects:
            data_post_profile_test = {
                post.text[:20]: self.post.text[:20],
                post.author.username: self.post.author.username,
                post.id: self.post.pk,
                post.pub_date: self.post.pub_date,
            }
            for value, exp in data_post_profile_test.items():
                with self.subTest(value=value):
                    self.assertEqual(
                        value,
                        exp,
                        msg='Неверные данные в context профиля'
                    )
        user = response.context['author']
        self.assertEqual(
            user.username,
            self.post.author.username,
            msg='Неверное отображение автора поста в профиле'
        )
        post_list = response.context['user']
        self.assertEqual(
            len(post_list.user.all()),
            len(self.user.user.all()),
            msg='Неверное количество постов в профиле'
        )

    def test_post_detail_correct_context(self):
        """
        Шаблон post_detail.html сформирован с правильным контекстом
        """
        response = self.auth.get(reverse(
            c.URL_NAME_POST_ID,
            kwargs={'post_id': self.post.id})
        )
        post = response.context['post']
        data_post_test = {
            post.text: self.post.text,
            post.author.username: self.post.author.username,
            post.pub_date: self.post.pub_date,
            post.group.title: self.post.group.title,
        }
        for value, exp in data_post_test.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    exp,
                    msg='Неверные данные в словаре контекста post_detail'
                )

        posts_count = response.context['post']
        self.assertEqual(
            len(posts_count.author.user.all()),
            len(self.post.author.user.all()),
            msg='Неверно отображается количество постов в post_detail'
        )

    def test_form_create_post_correct_context(self):
        """
        Шаблон create_post сформирован с правильным контекстом
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'group': self.group.id,
        }
        response = self.auth.post(
            reverse(c.URL_NAME_CREATE),
            data=form_data
        )
        self.assertRedirects(response, reverse(
            c.URL_NAME_PROFILE,
            kwargs={'username': self.user.username}),
            msg_prefix='Неверная переадресация после создания поста'
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            msg='Ошибка в создании поста'
        )

    def test_form_update_post_correct_context(self):
        """
        Шаблон update_post.html сформирован с правильным контекстом
        """
        form_data = {
            'text': 'поменяли чучуть',
            'group': self.group.id,
        }
        response = self.auth.post(reverse(
            c.URL_NAME_POST_EDIT,
            kwargs={'post_id': self.post.id}),
            data=form_data
        )
        self.assertRedirects(response, reverse(
            c.URL_NAME_POST_ID,
            kwargs={'post_id': self.post.id}),
            msg_prefix='Неверная переадресация после редактирования поста'
        )
        self.assertEqual(
            form_data['text'],
            get_object_or_404(Post, id=self.post.id).text,
            msg='Неудачное редактировние поста'
        )

    def test_in_group_post_index_create_correct(self):
        """
        Проверка корректности создания поста на главной странице
        при указании группы
        """
        posts_count = Post.objects.count()
        form_data = {
            'author': self.user.username,
            'text': 'Test text',
            'group': self.group.id,
            'slug': self.group.slug,
        }
        self.auth.post(
            reverse(c.URL_NAME_CREATE),
            data=form_data
        )
        response = self.auth.get(reverse(c.URL_NAME_INDEX))
        objects = response.context['page_obj']
        self.assertEqual(
            posts_count + 1,
            len(objects),
            msg='Пост не создаётся на главной странице'
        )

    def test_in_group_post_create_correct(self):
        """
        Проверка корректности создания поста на странице группы
        при указании группы
        """
        posts_count = Post.objects.count()
        form_data = {
            'author': self.user.username,
            'text': 'Test text',
            'group': self.group.id,
            'slug': self.group.slug,
        }
        self.auth.post(reverse(
            c.URL_NAME_CREATE),
            data=form_data
        )
        response = self.auth.get(reverse(
            c.URL_NAME_SLUG,
            kwargs={'slug': self.group.slug}),
        )
        objects = response.context['page_obj']
        self.assertEqual(
            posts_count + 1,
            len(objects),
            msg='Пост не создаётся на странице группы'
        )

    def test_in_profile_post_create_correct(self):
        """
        Проверка корректности создания поста на странице пользователя
        при указании группы
        """
        posts_count = Post.objects.count()
        form_data = {
            'author': self.user.username,
            'text': 'Test text',
            'group': self.group.id,
            'slug': self.group.slug,
        }
        self.auth.post(reverse(
            c.URL_NAME_CREATE),
            data=form_data
        )
        response = self.auth.get(reverse(
            c.URL_NAME_PROFILE,
            kwargs={'username': self.user.username}),
        )
        objects = response.context['page_obj']
        self.assertEqual(
            posts_count + 1,
            len(objects),
            msg='Пост не создаётся на странице пользователя'
        )

    def test_image_in_context_pages(self):
        """
        Проверяем, что картинка содержится в контексте к посту на страницах
        """
        page_list = {
            c.URL_NAME_INDEX: {},
            c.URL_NAME_SLUG: {'slug': self.group.slug},
            c.URL_NAME_PROFILE: {'username': self.user.username},
            c.URL_NAME_POST_ID: {'post_id': self.post.id},
        }
        for adress, slug in page_list.items():
            with self.subTest(adress=adress):
                response = self.auth.get(reverse(adress, kwargs=slug))
                self.assertTrue(response.context['post'].image)

    def test_comments_add_auth_users(self):
        """
        Проверяем, что пост может создавать только авторизованный пользователь
        """
        response_anon = self.client.get(reverse(
            c.URL_NAME_ADD_COMMENT,
            kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response_anon.status_code,
            HTTPStatus.FOUND,
            msg='Добавлять комментарии могут неавторизованные пользователи!')

    def test_correct_add_comment_to_post(self):
        """
        Проверяем, что комментарий добавляется к посту
        """
        Comment.objects.create(
            text='test',
            author=self.user,
            post=self.post
        )
        self.assertTrue(
            self.post.comments.all(),
            msg='Комментарий не появляется на странице поста')

    def test_auth_add_follows_and_delete(self):
        """
        Проверяем, что авторизованный пользователь подписывается и отписывается
        """
        self.auth.get(reverse(
            c.URL_NAME_PROFILE_FOLLOW,
            kwargs={'username': self.follow.username}
        ))
        self.assertEqual(
            Follow.objects.count(),
            1,
            msg='Авторизованный пользователь не подписывается!')
        self.auth.get(reverse(
            c.URL_NAME_PROFILE_UNFOLLOW,
            kwargs={'username': self.follow.username}
        ))
        self.assertEqual(
            Follow.objects.count(),
            0,
            msg='Авторизованный пользователь не отписывается!')

    def test_new_post_follow_add(self):
        """
        Проверяем что новый пост появляется у подписанного пользователя и
        не появляется у не подписанного
        """
        self.auth.get(reverse(
            c.URL_NAME_PROFILE_FOLLOW,
            kwargs={'username': self.follow.username}
        ))
        self.follower.post(reverse(
            c.URL_NAME_CREATE),
            data={'text': '123123'}
        )
        response_follow = self.auth.get(
            reverse(c.URL_NAME_FOLLOW)
        )
        response_unfollow = self.unfollower.get(
            reverse(c.URL_NAME_FOLLOW)
        )
        self.assertEqual(len(response_follow.context['page_obj']), 1)
        self.assertEqual(len(response_unfollow.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    """
    Тест кейс корректной работы паджинатора
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = mixer.blend(Group)
        Post.objects.bulk_create(
            [Post(
                author=cls.user,
                text=i,
                group=cls.group
            )
                for i in range(20)]
        )

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(self.user)
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """
        Проверка работы паджинатора 1 страницы
        """
        list_page = {
            c.URL_NAME_INDEX: {},
            c.URL_NAME_SLUG: {'slug': self.group.slug},
            c.URL_NAME_PROFILE: {'username': self.user.username},
        }
        for pattern, obj in list_page.items():
            with self.subTest(pattern=pattern):
                response = self.auth.get(reverse(
                    pattern,
                    kwargs=obj))
                self.assertEqual(len(
                    response.context['page_obj']),
                    10,
                    msg='Неверное количество постов 1 страницы паджинатора'
                )

    def test_second_page_contains_three_records(self):
        """
        Проверка работы паджинатора 2 страницы
        """
        list_page = {
            c.URL_NAME_INDEX: {},
            c.URL_NAME_SLUG: {'slug': self.group.slug},
            c.URL_NAME_PROFILE: {'username': self.user.username},
        }
        for pattern, obj in list_page.items():
            with self.subTest(pattern=pattern):
                response = self.auth.get(reverse(
                    pattern,
                    kwargs=obj) + '?page=2')
                self.assertEqual(len(
                    response.context['page_obj']),
                    10,
                    msg='Неверное количество постов 2 страницы паджинатора'
                )


class TestCacheYatube(TestCase):
    """
    Тест кейс кеша в проекте Yatube
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = mixer.blend(Group)

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(self.user)

    def test_cache_index(self):
        """
        Проверяем кеш index.html
        """
        self.auth.post(
            reverse(c.URL_NAME_CREATE),
            data={'text': 'Тест кеша'}
        )
        response = self.auth.get(reverse(c.URL_NAME_INDEX))
        self.assertEqual(len(
            response.context['page_obj']),
            1
        )
        Post.objects.filter(id=1).delete()
        response_after_delete_post = self.auth.get(reverse(c.URL_NAME_INDEX))
        self.assertEqual(
            response_after_delete_post.content,
            response.content
        )
        cache.clear()
        response_after_delete_cache = self.auth.get(reverse(c.URL_NAME_INDEX))
        self.assertEqual(len(
            response_after_delete_cache.context['page_obj']),
            0
        )
