from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group
from django.core.cache import cache
from http import HTTPStatus

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='PostAuthor')
        cls.random_user = User.objects.create_user(username='Random_user')
        cls.post = Post.objects.create(
            id='9999',
            author=cls.author
        )
        cls.group = Group.objects.create(slug='test_slug')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_random = Client()
        self.authorized_random.force_login(PostURLTests.random_user)
        self.authorized_author = Client()
        self.authorized_author.force_login(PostURLTests.author)

    def tearDown(self):
        cache.clear()

    def test_urls_exist_at_desired_location_with_auth_check(self):
        """Страница успешно открывается с учетом прав доступа."""
        url = {
            '/': self.guest_client,
            '/group/test_slug/': self.guest_client,
            '/profile/PostAuthor/': self.guest_client,
            '/posts/9999/': self.guest_client,
            '/posts/9999/edit/': self.authorized_author,
            '/create/': self.authorized_random,
            '/follow/': self.authorized_random
        }
        for url, client in url.items():
            with self.subTest(url=url, client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_returns_404(self):
        """Несуществующая страница возвращает ошибку 404,."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/PostAuthor/': 'posts/profile.html',
            '/posts/9999/': 'posts/post_detail.html',
            '/posts/9999/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_create_page_url_for_guest_redirects_to_login(self):
        """URL-адрес страницы создания поста переадресует
        неавторизованного пользователя на страницу авторизации."""
        response = self.guest_client.get('/create/')
        url_create_redirect = '/auth/login/?next=/create/'
        self.assertRedirects(response, url_create_redirect)

    def test_edit_page_url_for_guest_redirects_to_login(self):
        """URL-адрес страницы редактирования поста переадресует
        неавторизованного пользователя на страницу авторизации."""
        response = self.guest_client.get('/posts/9999/edit/')
        url_edit_redirect = '/auth/login/?next=/posts/9999/edit/'
        self.assertRedirects(response, url_edit_redirect)

    def test_edit_page_url_for_non_author_redirects_to_post_details(self):
        """URL-адрес страницы редактирования поста переадресует
        не автора поста на страницу информации о посте."""
        response = self.authorized_random.get('/posts/9999/edit/')
        url_edit_redirect = '/posts/9999/'
        self.assertRedirects(response, url_edit_redirect)

    def test_follow_url_redirects_to_author_profile(self):
        """URL-адрес функции подписки на автора переадресует
        на страницу профиля автора поста."""
        response = self.authorized_random.get('/profile/PostAuthor/follow/')
        url_edit_redirect = '/profile/PostAuthor/'
        self.assertRedirects(response, url_edit_redirect)

    def test_unfollow_url_redirects_to_author_profile(self):
        """URL-адрес функции отписки от автора переадресует
        на страницу профиля автора поста."""
        response = self.authorized_random.get('/profile/PostAuthor/unfollow/')
        url_edit_redirect = '/profile/PostAuthor/'
        self.assertRedirects(response, url_edit_redirect)

    def test_add_comment_url_redirects_to_post_details(self):
        """URL-адрес функции добавления комментария
        переадресует на страницу информации о посте."""
        response = self.authorized_random.get('/posts/9999/comment/')
        url_edit_redirect = '/posts/9999/'
        self.assertRedirects(response, url_edit_redirect)
