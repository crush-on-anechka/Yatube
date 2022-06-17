from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post
from django.core.cache import cache

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user
        )
        cls.client = Client()

    def test_index_page_saved_in_cache(self):
        '''Главная страница сохраняется в кэше'''
        response_pre = self.client.get(reverse('posts:index'))
        posts_count = Post.objects.count()
        self.post.delete()
        self.assertEqual(Post.objects.count(), posts_count - 1)
        response_post = self.client.get(reverse('posts:index'))
        self.assertEqual(response_pre.content, response_post.content)
        cache.clear()
        response_cleared = self.client.get(reverse('posts:index'))
        self.assertNotEqual(
            response_pre.content,
            response_cleared.content
        )
