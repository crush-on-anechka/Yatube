from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from posts.models import Post, Group, Comment
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import shutil
import tempfile

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='PostAuthor')
        cls.random_user = User.objects.create_user(username='RandomUser')
        cls.group = Group.objects.create(slug='test_slug')
        cls.post = Post.objects.create(
            id=9999,
            author=cls.author,
            text='TestText',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_random = Client()
        self.authorized_random.force_login(self.random_user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00\x01\x00\x80'
            b'\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04'
            b'\x00\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x02'
            b'\x00\x01\x00\x00\x02\x02\x0C\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_and_redirect_to_profile(self):
        """Валидная форма создает запись
        и перенаправляет на страницу профиля автора."""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group,
            'image': self.uploaded
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                image='posts/small.gif'
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.author.username}
        ))

    def test_edit_post_and_redirect_to_profile(self):
        """Валидная форма редактирует запись и
        перенаправляет на страницу информации о посте."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'TestEditedText',
            'group': self.group,
            'image': self.uploaded
        }
        response = self.authorized_author.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text='TestEditedText',
                image='posts/small.gif'
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_page_for_guest_redirects_to_login(self):
        """Страница создания поста переадресует неавторизованного
        пользователя на страницу авторизации."""
        response = self.guest_client.get(reverse('posts:post_create'))
        url_create_redirect = '/auth/login/?next=/create/'
        self.assertRedirects(response, url_create_redirect)

    def test_edit_page_for_guest_redirects_to_login(self):
        """Страница редактирования поста переадресует неавторизованного
        пользователя на страницу авторизации."""
        response = self.guest_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        ))
        url_edit_redirect = '/auth/login/?next=/posts/9999/edit/'
        self.assertRedirects(response, url_edit_redirect)

    def test_edit_page_for_non_author_redirects_to_post_details(self):
        """Страница редактирования поста переадресует
        не автора поста на страницу информации о посте."""
        response = self.authorized_random.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        ))
        url_edit_redirect = '/posts/9999/'
        self.assertRedirects(response, url_edit_redirect)


class PostCommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            id=9999,
            author=cls.user,
            text='TestText',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_added_to_post_and_redirect_to_post_detail(self):
        """Валидная форма создает комментарий авторизованного пользователя
        под выбранным постом и переадресует на страницу информации о посте."""
        comments_count = Comment.objects.count()
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data={'text': 'TestComment'},
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(
                text='TestComment',
                post=self.post
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_comment_unavailable_for_guest_and_redirect_to_login(self):
        """Комментирование поста недоступно неавторизованному
        пользователю, переадресация на страницу авторизации."""
        comments_count = Comment.objects.count()
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data={'text': 'TestComment'},
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertRedirects(
            response,
            '/auth/login/?next=/posts/9999/comment/'
        )
