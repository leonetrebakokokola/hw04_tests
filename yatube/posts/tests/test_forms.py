from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group

User = get_user_model()


class FormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(title='test-group')
        cls.post = Post.objects.create(
            text='test-post',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test-post',
            'author': self.user,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            Post.objects.filter(text='test-post').first().text,
            form_data['text']
        )
        self.assertEqual(
            Post.objects.filter(text='test-post').first().author,
            form_data['author']
        )
        self.assertEqual(
            Post.objects.filter(text='test-post').first().group.id,
            form_data['group']
        )
        # self.assertTrue(Post.objects.filter(text='test-post').exists())

    def test_edit_post(self):
        form_data_edit = {
            'text': 'test-post-edit',
            'author': self.user,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            ),
            data=form_data_edit,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'post', kwargs={'username': 'test-user', 'post_id': self.post.id}))
        self.assertEqual(
            Post.objects.filter(text='test-post-edit').first().text,
            form_data_edit['text']
        )
        self.assertEqual(
            Post.objects.filter(text='test-post-edit').first().author,
            form_data_edit['author']
        )
        self.assertEqual(
            Post.objects.filter(text='test-post-edit').first().group.id,
            form_data_edit['group']
        )
