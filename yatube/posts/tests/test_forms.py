from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Tester')
        group1 = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание группы',
            slug='test-slug'
        )

        cls.group = group1
        cls.post = Post.objects.create(
            text='TestPost',
            author=cls.user,
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='Test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новую запись."""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)

        self.assertRedirects(response,
                             reverse('posts:profile',
                                     args=(self.user.username,)))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(group=self.group.id,
                                            text='Тестовый текст').exists())

    def test_edit_post(self):
        """Валидная форма редактирует запись и производит редирект."""
        test_post = Post.objects.create(
            text='Тестовый текст записи',
            author=self.user,
        )
        posts_count = Post.objects.count()
        form_data_edit = {
            'group': self.group.id,
            'text': 'Измененный текст записи',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': test_post.id}),
            data=form_data_edit)
        test_post.refresh_from_db()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': test_post.id}))
        self.assertTrue(Post.objects.filter(
            text='Измененный текст записи',
            group=self.group.id).exists())

    def test_authorized_user_comment(self):
        """Авторизованный юзер может комментить"""
        form_data = {
            'text': 'Test-text',
            'author': self.user,
            'post': self.post
        }

        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': self.post.id
                }),
            data=form_data,
            follow=True
        )
        new_comment = response.context['comments']
        self.assertEqual(new_comment[0].text, form_data['text'])

    def test_unauthorized_user_cant_comment(self):
        """Не авторизованный юзер не может комментить"""
        form_data = {
            'text': 'Test-text',
            'author': self.user,
            'post': self.post
        }
        self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': self.post.id
                }),
            data=form_data,
            follow=True
        )

        self.assertEqual(0, self.post.comments.count())
