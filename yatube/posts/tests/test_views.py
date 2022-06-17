from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from posts.models import Post, Group, Follow
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache
import shutil
import tempfile

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='PostAuthor')
        cls.random_user = User.objects.create_user(username='RandomUser')
        cls.group = Group.objects.create(
            title='Test title',
            slug='test_slug'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00\x01\x00\x80'
            b'\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04'
            b'\x00\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x02'
            b'\x00\x01\x00\x00\x02\x02\x0C\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            id=9999,
            author=cls.author,
            text='Test text',
            group=cls.group,
            image=cls.uploaded
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_random = Client()
        self.authorized_random.force_login(self.random_user)

    def tearDown(self):
        cache.clear()

    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_use_correct_template_with_auth_check(self):
        """Страница использует соответствующий
        шаблон и учитывает права доступа."""
        guest = self.guest_client
        auth = self.authorized_author
        random = self.authorized_random
        templates_pages_names = [
            (reverse('posts:index'), 'posts/index.html', guest),
            (reverse('posts:post_create'), 'posts/create_post.html', random),
            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ), 'posts/group_list.html', guest),
            (reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            ), 'posts/profile.html', guest),
            (reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ), 'posts/post_detail.html', guest),
            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ), 'posts/create_post.html', auth)
        ]
        for reverse_name, template, client in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.slug
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.author.username)
        self.assertEqual(post_group_0, self.group.slug)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        ))
        self.assertEqual(
            response.context['group'].slug,
            self.group.slug
        )
        self.assertEqual(
            response.context['page_obj'][0].text,
            self.post.text
        )
        self.assertEqual(
            response.context['page_obj'][0].author.username,
            self.author.username
        )
        self.assertEqual(
            response.context['page_obj'][0].group.title,
            self.group.title
        )
        self.assertEqual(
            response.context['page_obj'][0].image,
            'posts/small.gif'
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse(
            'posts:profile',
            kwargs={'username': self.author}
        ))
        self.assertEqual(
            response.context['author'].username, self.author.username
        )
        self.assertEqual(
            response.context['quantity'], 1
        )
        self.assertEqual(
            response.context['page_obj'][0].text, self.post.text
        )
        self.assertEqual(
            response.context['page_obj'][0].author.username,
            self.author.username
        )
        self.assertEqual(
            response.context['page_obj'][0].group.title, self.group.title
        )
        self.assertEqual(
            response.context['page_obj'][0].image, 'posts/small.gif'
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(response.context['quantity'], 1)
        self.assertEqual(response.context['edit_visible'], True)
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(
            response.context['post'].author.username, self.author.username
        )
        self.assertEqual(
            response.context['post'].group.title, self.group.title
        )
        self.assertEqual(
            response.context['post'].image, 'posts/small.gif'
        )

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        ))
        self.assertIsInstance(
            response.context['form'].fields['text'],
            forms.fields.CharField
        )
        self.assertIsInstance(
            response.context['form'].fields['group'],
            forms.fields.ChoiceField
        )
        self.assertIsInstance(
            response.context['form'].fields['image'],
            forms.fields.ImageField
        )
        self.assertEqual(response.context['is_edit'], True)
        self.assertEqual(response.context['post_id'], self.post.id)

    def test_edit_page_for_non_author_redirects_to_post_details(self):
        """Страница редактирования поста переадресует
        не автора поста на страницу информации о посте."""
        response = self.authorized_random.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ))
        url_edit_redirect = '/posts/9999/'
        self.assertRedirects(response, url_edit_redirect)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(slug='test_slug')
        cls.post = Post.objects.bulk_create(
            [Post(author=cls.user, group=cls.group) for i in range(1, 14)]
        )
        cls.guest_client = Client()

    def tearDown(self):
        cache.clear()

    def test_index_first_page_contains_ten_records(self):
        """Первая страница шаблона index отображает 10 записей."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        """Вторая страница шаблона index отображает 3 записи."""
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        """Первая страница шаблона group_list отображает 10 записей."""
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        ))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        """Вторая страница шаблона group_list отображает 3 записи."""
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        """Первая страница шаблона profile отображает 10 записей."""
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        """Вторая страница шаблона profile отображает 3 записи."""
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)


class PostCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.correct_group = Group.objects.create(slug='correct_slug')
        cls.wrong_group = Group.objects.create(slug='wrong_slug')
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user,
            group=cls.correct_group
        )
        cls.client = Client()

    def test_post_in_group_shown_on_index(self):
        """Пост, при создании которого указывается группа,
        показывается на странице index."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][0].text,
            self.post.text
        )
        self.assertEqual(
            response.context['page_obj'][0].group.slug,
            self.correct_group.slug
        )

    def test_post_in_group_shown_on_group_page(self):
        """Пост, при создании которого указывается группа,
        показывается на странице группы."""
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.correct_group.slug}
        ))
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)

    def test_post_in_group_shown_in_author_profile(self):
        """Пост, при создании которого указывается группа,
        показывается в профайле автора."""
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(
            response.context['page_obj'][0].text,
            self.post.text
        )
        self.assertEqual(
            response.context['page_obj'][0].group.slug,
            self.correct_group.slug
        )

    def test_post_in_group_is_not_shown_on_wrong_group_page(self):
        """Пост, при создании которого указывается группа,
        не показывается на странице другой группы."""
        response = self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.wrong_group.slug}
        ))
        with self.assertRaises(IndexError):
            self.assertEqual(
                response.context['page_obj'][0].text,
                self.post.text
            )


class FollowsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='PostAuthor')
        cls.follower = User.objects.create_user(username='Follower')
        cls.post = Post.objects.create(
            author=cls.author
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_follow_and_unfollow_work_and_redirect_to_profile(self):
        """Функция подписки/отписки создает/удаляет связь подписчик-автор
        и переадресует на страницу профиля автора."""
        redirect_destination = reverse(
            'posts:profile',
            kwargs={'username': self.author.username}
        )
        follows_count = Follow.objects.count()
        response = self.authorized_follower.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author.username}
        ))
        self.assertTrue(Follow.objects.get(
            user=self.follower,
            author=self.author
        ))
        self.assertEqual(Follow.objects.count(), follows_count + 1)
        self.assertRedirects(response, redirect_destination)
        response = self.authorized_follower.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.author.username}
        ))
        self.assertEqual(Follow.objects.count(), follows_count)
        self.assertRedirects(response, redirect_destination)

    def test_follow_index_page_shows_following_posts_to_follower(self):
        """Страница избранных авторов показывает посты только
        тех авторов, на которых пользователь подписан."""
        Follow.objects.create(user=self.follower, author=self.author)
        response = self.authorized_follower.get(reverse(
            'posts:follow_index'
        ))
        self.assertEqual(
            response.context['page_obj'][0],
            self.post
        )
        response = self.authorized_author.get(reverse(
            'posts:follow_index'
        ))
        self.assertEqual(len(response.context['page_obj']), 0)
