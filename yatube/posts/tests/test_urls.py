from http import HTTPStatus
from urllib.parse import urljoin

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Test_name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание тестовой группы',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = self.post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_opened_pages(self):
        """Страницы доступные всем"""
        url_names = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/',
        )
        for address in url_names:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_and_edit_for_authorized_user(self):
        """Страницы доступные авторизованному пользователю."""
        url_names = (
            '/create/',
            f'/posts/{self.post.id}/edit/',
            '/follow/'
        )
        for address in url_names:
            with self.subTest():
                response = self.authorized_client.get(address)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_url(self):
        """без авторизации приватные URL недоступны"""
        url_names = (
            '/create/',
            f'/posts/{self.post.id}/edit/',
            '/follow/'
        )
        for address in url_names:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_redirect_anonymous_on_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(reverse('posts:post_create'))
        url = urljoin(reverse('users:login'), '?next=/create/')
        self.assertRedirects(response, url)

    def test_follow_redirect_anonymous_on_login(self):
        """Страница /follow/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(reverse('posts:follow_index'))
        url = urljoin(reverse('users:login'), '?next=/follow/')
        self.assertRedirects(response, url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        for template, url in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                self.assertTemplateUsed(response, url)

    def test_page_404(self):
        response = self.guest_client.get('/404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_errors_uses_correct_template(self):
        response404 = self.guest_client.get('/404/')
        self.assertTemplateUsed(response404, 'core/404.html')
