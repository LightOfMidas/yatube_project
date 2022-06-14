import shutil

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post, User


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

        cls.group1 = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Описание тестовой группы 1',
        )
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug-1',
            description='Описание тестовой группы 2',
        )
        cls.user1 = User.objects.create(username='Test_name1')

        cls.count = 3

        cls.post = Post.objects.create(
            author=cls.user1,
            text='Тестовый текст',
            group=cls.group1,
            image=uploaded
        )
        posts = [Post(
            author=cls.user1,
            group=cls.group2,
            text='Тестовый текст',
            image=uploaded) for i in range(cls.count)]
        Post.objects.bulk_create(posts)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='Test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        post_author_0 = first_post.author.username
        post_text_0 = first_post.text
        post_group_0 = first_post.group
        post_image_0 = Post.objects.first().image

        self.assertCountEqual(post_image_0, self.post.image)
        self.assertEqual(post_author_0, self.user1.username)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0.title, self.group2.title)

    def test_group_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:group_list',
                                         kwargs={'slug': self.group1.slug}))
        response_group = response.context['group']
        post_image_0 = Post.objects.first().image

        self.assertCountEqual(post_image_0, self.post.image)
        self.assertEqual(response_group.title, self.group1.title)
        self.assertEqual(response_group.description,
                         self.group1.description)
        self.assertEqual(response_group.slug, self.group1.slug)

    def test_create_post_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        edit_flag = response.context.get('is_edit')

        self.assertFalse(edit_flag)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:profile',
                                         kwargs={'username': self.user1}))

        page_obj = response.context['page_obj'][0]
        post_author = response.context.get('profile').username
        post_text_0 = page_obj.text
        post_image_0 = Post.objects.first().image

        self.assertCountEqual(post_image_0, self.post.image)
        self.assertEqual(post_author, self.user1.username)
        self.assertEqual(post_text_0, self.post.text)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        test_post = Post.objects.create(text='Тестовый текст 1',
                                        author=self.user,
                                        image=self.post.image)
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={
                                                  'post_id': test_post.id}))

        post_author = response.context.get('post').author.username
        post_text_0 = response.context.get('post')
        post_image_0 = test_post.image
        self.assertCountEqual(post_image_0, self.post.image)
        self.assertEqual(post_author, self.user.username)
        self.assertEqual(post_text_0, test_post)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        test_post = Post.objects.create(text='Тестовый текст 1',
                                        author=self.user,)
        response = self.authorized_client.get(reverse('posts:post_edit',
                                              kwargs={
                                                  'post_id': test_post.id}))
        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        edit_flag = response.context.get('is_edit')
        self.assertTrue(edit_flag)

    def test_new_post_index(self):
        """Новая запись появляется на главной странице сайта."""
        response = self.client.get(reverse('posts:index'))
        self.assertContains(response, self.post)

    def test_new_post_profile(self):
        """Новая запись появляется на персональной странице пользователя."""
        response = self.client.get(reverse('posts:profile',
                                           kwargs={'username':
                                                   self.user1.username}))
        self.assertContains(response, self.post)

    def test_new_post_group_list(self):
        """Новая запись появляется на отдельной странице группы поста."""
        response = self.client.get(reverse('posts:group_list',
                                           kwargs={'slug': self.group1.slug}))
        self.assertContains(response, self.post)

    def test_post_another_group(self):
        """Пост не попал в другую группу."""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group2.slug}))
        left_group = response.context['page_obj']
        self.assertNotIn(self.post, left_group)

    def test_authorized_user_follow(self):
        """ Тестирование подписки """
        follow_count = Follow.objects.count()
        new_user = User.objects.create(username='NewUser')
        new_authorized_client = Client()
        new_authorized_client.force_login(new_user)

        new_authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))

        follow_obj = Follow.objects.get(author=self.user, user=new_user)
        self.assertIsNotNone(follow_obj)
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_authorized_user_unfollow(self):
        """ Тестирование отписки """
        new_user = User.objects.create(username='NewUser')
        new_authorized_client = Client()
        new_authorized_client.force_login(new_user)

        Follow.objects.create(author=self.user, user=new_user)
        follow_count = Follow.objects.count()
        new_authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_following_posts_show(self):
        """ Отображение постов отслеживаемых авторов """
        new_user = User.objects.create(username='Tester223')
        new_authorized_client = Client()
        new_authorized_client.force_login(new_user)

        new_authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user1.username}
        ))

        response = new_authorized_client.get(reverse('posts:follow_index'))
        following_post = response.context['page_obj'].object_list[0]
        self.assertEqual(following_post.text, self.post.text)

    def test_cache(self):
        " Кэш "
        pre_response = self.authorized_client.get(reverse('posts:index'))
        post = Post.objects.create(text='test', author=self.user)
        response_after = self.authorized_client.get(reverse('posts:index'))
        Post.objects.filter(id=post.id).delete()
        response_after_delete = self.authorized_client.get(
            reverse('posts:index'))
        self.assertEqual(response_after.content, response_after_delete.content)
        cache.clear()
        response_after_clear = self.authorized_client.get(
            reverse('posts:index'))
        self.assertEqual(
            response_after_clear.context['paginator'].count,
            pre_response.context['paginator'].count)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name')
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug2',
            description='Тестовое описание')
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group))
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        list_urls = ({
            reverse('posts:index'): 'index',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug2'}): 'group_list',
            reverse('posts:profile',
                    kwargs={'username': 'test_name'}): 'profile',
        })
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len
                             (response.context.get
                              ('page_obj').object_list), 10)

    def test_second_page_contains_three_posts(self):
        list_urls = ({
            reverse('posts:index') + '?page=2': 'index',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug2'}) + '?page=2':
            'group_list',
            reverse('posts:profile',
                    kwargs={'username': 'test_name'}) + '?page=2':
            'profile',
        })
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len
                             (response.context.get('page_obj').object_list), 3)
