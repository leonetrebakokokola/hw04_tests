from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post
from django import forms

User = get_user_model()


class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(slug='test-slug')
        cls.groupTwo = Group.objects.create(slug='test-slug-2')
        cls.post = Post.objects.create(
            text='test-post',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('index'),
            'posts/group.html': (
                reverse('group_posts', kwargs={'slug': self.group.slug})
            ),
            'posts/new_post.html': reverse('new_post'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        response = self.authorized_client.get(reverse('index'))
        first_post = response.context['page'][0]
        self.assertEqual(first_post.text, 'test-post')

    def test_group_context(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug}))
        first_post = response.context['page'][0]
        self.assertEqual(first_post.text, 'test-post')
        self.assertEqual(response.context['group'].slug, 'test-slug')

    def test_new_post_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {'text': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )
        form_fields = {'text': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_user_profile_context(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username}))
        first_post = response.context['page'][0]
        self.assertEqual(first_post.text, 'test-post')

    def test_post_context(self):
        response = self.authorized_client.get(
            reverse(
                'post',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )
        post = response.context['post']
        self.assertEqual(post.text, 'test-post')

    # Проверка есть ли пост на главной и на страницы группы
    def test_post_on_page(self):
        pages_names = {
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.groupTwo.slug})
        }
        for adress in pages_names:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                for post in response.context.get('page').object_list:
                    self.assertEqual(post.text, 'test-post')

    # Проверка чтоб пост не был на не нужной страницы группы
    def test_post_not_another_group_page(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.groupTwo.slug}))
        self.assertEqual(
            str(response.context.get('page').object_list), '<QuerySet []>')


class PaginatorViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(slug='test-slug')

        for x in range(13):
            Post.objects.create(
                text=f'test-post-{x}',
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_first_page(self):
        pages_names = {
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.user.username}),
        }
        for adress in pages_names:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(len(response.context.get('page')), 10)

    def test_paginator_second_page(self):
        pages_names = {
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.user.username}),
        }
        for adress in pages_names:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress + '?page=2')
                self.assertEqual(len(response.context.get('page')), 3)
