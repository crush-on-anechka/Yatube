from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post, Group, Comment, Follow

User = get_user_model()

POST_STR_LENGTH: int = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост НАДО ИСПРАВИТЬ',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user2,
        )

    def test_models_have_correct_object_names(self):
        """У моделей корректно работает __str__."""
        str_values = {
            self.group: self.group.title,
            self.post: self.post.text[:POST_STR_LENGTH],
            self.comment: self.comment.text,
            self.follow: f'{self.user.username} -> {self.user2.username}'
        }
        for field, expected_value in str_values.items():
            with self.subTest(field=field):
                self.assertEqual(expected_value, str(field))

    def test_post_models_have_correct_verbose_names(self):
        """У моделей корректно работают verbose names."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        follow = PostModelTest.follow
        verboses = [
            (post, 'text', 'Текст поста'),
            (post, 'pub_date', 'Дата публикации'),
            (post, 'author', 'Автор поста'),
            (post, 'group', 'Группа, к которой относится пост'),
            (post, 'image', 'Картинка'),
            (group, 'title', 'title'),
            (group, 'slug', 'identificator'),
            (group, 'description', 'description'),
            (comment, 'post', 'Пост'),
            (comment, 'text', 'Текст комментария'),
            (comment, 'created', 'Дата комментария'),
            (comment, 'author', 'Автор поста'),
            (follow, 'user', 'Подписчик'),
            (follow, 'author', 'Автор'),
        ]
        for model, field, expected_value in verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    model._meta.get_field(field).verbose_name, expected_value)
