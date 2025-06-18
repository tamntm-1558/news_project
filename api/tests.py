from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

def get_token_for_user(user):
    return str(RefreshToken.for_user(user).access_token)

class BaseAPITestCase(APITestCase):
    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

class RegisterAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.url = reverse('user-register')
        self.valid_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPassword123',
        }

    def test_register_success(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data['user'])
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_fail_missing_username(self):
        data = {'username': '', 'email': 'invalidemail', 'password': 'short'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ['username', 'email', 'password']:
            self.assertIn(field, response.data)

class LoginAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.url = reverse('user-login')
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123'
        )

    def test_login_success(self):
        data = {'email': 'testuser@example.com', 'password': 'TestPassword123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data['user'])

    def test_login_fail_invalid_email(self):
        data = {'email': 'invalidemail', 'password': 'TestPassword123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Enter a valid email address.', response.data['email'])

    def test_login_fail_nonexistent_email(self):
        data = {'email': 'notexist@example.com', 'password': 'TestPassword123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid credentials.', response.data['non_field_errors'])

class CommentListCreateAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123'
        )
        self.article = self.user.articles.create(
            slug='test-article',
            title='Test Article',
            description='This is a test article.',
            body='This is the body of the test article.'
        )
        self.token = get_token_for_user(self.user)
        self.url = reverse('comments-list-create', kwargs={'article_id': self.article.id})
        self.valid_data = {'body': 'This is a test comment.'}
        self.invalid_data = {'body': ''}

    def test_create_comment_success(self):
        self.authenticate(self.token)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('body', response.data)
        self.assertEqual(response.data['body'], self.valid_data['body'])

    def test_create_comment_fail_blank_body(self):
        self.authenticate(self.token)
        response = self.client.post(self.url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', response.data['body'])

    def test_create_comment_fail_unauthenticated(self):
        self.client.credentials()
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', response.data['detail'])

    def test_list_comments_success(self):
        self.test_create_comment_success()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['count'], 0)
        self.assertIn(self.valid_data['body'], [comment['body'] for comment in response.data['results']])

class CommentDetailAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123'
        )
        self.article = self.user.articles.create(
            title='Test Article',
            description='This is a test article.',
            body='This is the body of the test article.'
        )
        self.comment = self.article.comments.create(
            author=self.user,
            body='This is a test comment.'
        )
        self.url = reverse('comments-detail', kwargs={'article_id': self.article.id, 'comment_id': self.comment.id})
        self.token = get_token_for_user(self.user)
        self.valid_data = {'body': 'This is an updated comment.'}
        self.invalid_data = {'body': ''}

    def test_update_comment_success(self):
        self.authenticate(self.token)
        response = self.client.put(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('body', response.data)
        self.assertEqual(response.data['body'], self.valid_data['body'])

    def test_update_comment_fail_blank_body(self):
        self.authenticate(self.token)
        response = self.client.put(self.url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', response.data['body'])

    def test_update_comment_fail_unauthenticated(self):
        self.client.credentials()
        response = self.client.put(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', response.data['detail'])

    def test_delete_comment_success(self):
        self.authenticate(self.token)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.article.comments.filter(id=self.comment.id).exists())

    def test_delete_comment_fail_unauthenticated(self):
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', response.data['detail'])

    def test_delete_comment_fail_not_found(self):
        self.authenticate(self.token)
        invalid_url = reverse('comments-detail', kwargs={'article_id': self.article.id, 'comment_id': 9999})
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No Comment matches the given query.', response.data['detail'])

class ArticleAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123'
        )
        self.token = get_token_for_user(self.user)
        self.url = reverse('articles-list')
        self.valid_data = {
            'slug': 'test-article',
            'title': 'Test Article',
            'description': 'This is a test article.',
            'body': 'This is the body of the test article.'
        }
        self.invalid_data = {
            'slug': '',
            'title': '',
            'description': '',
            'body': ''
        }

    def test_create_article_success(self):
        self.authenticate(self.token)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('slug', response.data)
        self.assertEqual(response.data['title'], self.valid_data['title'])
        self.assertEqual(response.data['slug'], self.valid_data['slug'])
        self.assertEqual(response.data['description'], self.valid_data['description'])
        self.assertEqual(response.data['body'], self.valid_data['body'])

    def test_create_article_fail_blank_fields(self):
        self.authenticate(self.token)
        response = self.client.post(self.url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ['slug', 'title', 'description', 'body']:
            self.assertIn(field, response.data)

    def test_list_articles_success(self):
        self.authenticate(self.token)
        self.test_create_article_success()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)
        self.assertIn('title', response.data['results'][0])
        self.assertIn('description', response.data['results'][0])

    def test_retrieve_article_success(self):
        self.authenticate(self.token)
        article = self.user.articles.create(**self.valid_data)
        url = reverse('articles-detail', kwargs={'pk': article.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], self.valid_data['title'])
        self.assertEqual(response.data['description'], self.valid_data['description'])
        self.assertEqual(response.data['body'], self.valid_data['body'])

    def test_retrieve_article_fail_not_found(self):
        self.authenticate(self.token)
        url = reverse('articles-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No Article matches the given query.', response.data['detail'])

    def test_update_article_success(self):
        self.authenticate(self.token)
        article = self.user.articles.create(**self.valid_data)
        url = reverse('articles-detail', kwargs={'pk': article.id})
        updated_data = {'title': 'Updated Title', 'slug': 'updated-slug', 'description': 'Updated Description', 'body': 'Updated Body'}
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], updated_data['title'])
        self.assertEqual(response.data['slug'], updated_data['slug'])
        self.assertEqual(response.data['description'], updated_data['description'])
        self.assertEqual(response.data['body'], updated_data['body'])

    def test_update_article_fail_blank_fields(self):
        self.authenticate(self.token)
        article = self.user.articles.create(**self.valid_data)
        url = reverse('articles-detail', kwargs={'pk': article.id})
        response = self.client.put(url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ['slug', 'title', 'description', 'body']:
            self.assertIn(field, response.data)

    def test_update_article_fail_unauthenticated(self):
        article = self.user.articles.create(**self.valid_data)
        url = reverse('articles-detail', kwargs={'pk': article.id})
        self.client.credentials()
        response = self.client.put(url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', response.data['detail'])

    def test_delete_article_success(self):
        self.authenticate(self.token)
        article = self.user.articles.create(**self.valid_data)
        url = reverse('articles-detail', kwargs={'pk': article.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.user.articles.filter(id=article.id).exists())

    def test_delete_article_fail_unauthenticated(self):
        article = self.user.articles.create(**self.valid_data)
        url = reverse('articles-detail', kwargs={'pk': article.id})
        self.client.credentials()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', response.data['detail'])

    def test_delete_article_fail_not_found(self):
        self.authenticate(self.token)
        url = reverse('articles-detail', kwargs={'pk': 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No Article matches the given query.', response.data['detail'])
