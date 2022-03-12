# deals/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=f'Тестовая группа',
            slug=f'test-slug',
            description=f'Тестовое описание группы',
        )
        cls.group2 = Group.objects.create(
            title=f'Тестовая группа 2',
            slug=f'test-slug-2',
            description=f'Тестовое описание группы 2',
        )
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post.objects.create(
            author=cls.user,
            text=f'Тестовый текст поста {i}',
            group=cls.group,
        ))

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/profile.html': reverse('posts:profile', kwargs={'username': 'auth'}),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={'post_id': 1}),
            'posts/create_post.html': reverse('posts:post_edit', kwargs={'post_id': 1}),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ),
        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


    # Проверка словаря контекста главной страницы (в нём передаётся паджинатор)
    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10. 
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    # Проверка словаря контекста страницы списка групп (в нём передаётся паджинатор)
    def test_first_group_list_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        # Проверка: количество постов на первой странице равно 10. 
        self.assertEqual(len(response.context['page_obj']), 10)
        
    def test_second_group_list_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:group_list', kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    # Проверка словаря контекста страницы списка постов пользователя (в нём передаётся паджинатор)
    def test_first_profile_list_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:profile', kwargs={'username': 'auth'}))
        # Проверка: количество постов на первой странице равно 10. 
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_list_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:profile', kwargs={'username': 'auth'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    # Проверяем, что словарь context страницы /post_detail
    # в первом элементе списка object_list содержит ожидаемые значения 
    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail', kwargs={'post_id': 1}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['post']
        post_text = first_object.text
        post_group_title = first_object.group.title
        post_author_username = first_object.author.username
        self.assertEqual(post_text, 'Тестовый текст поста 0')
        self.assertEqual(post_group_title, 'Тестовая группа')
        self.assertEqual(post_author_username, 'auth')

    def test_existing_post_some_pages(self):
        tests_pages = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': reverse('posts:profile', kwargs={'username': 'auth'}),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug-2'})
            ),
        }
        for template, page in tests_pages.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                result = False
                for post in response.context['page_obj']:
                    post_text = post.text
                    post_group_title = post.group.title
                    post_author_username = post.author.username        
                    if post_text == 'Тестовый текст поста 12' and post_group_title == 'Тестовая группа' and post_author_username == 'auth':
                        result = True
                        break
                if post_group_title == "Тестовая группа 2":
                    self.assertFalse(result)
                else:
                    self.assertTrue(result)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон /edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit', kwargs={'post_id': 1}))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField 
            # преобразуются в CharField с виджетом forms.Textarea           
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }        

        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_create_post_page_show_correct_context(self):
        """Шаблон /create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField 
            # преобразуются в CharField с виджетом forms.Textarea           
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)