import os
from django.urls import reverse
from rest_framework.test import APITestCase # type: ignore
from rest_framework import status # type: ignore
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from ..models import User

User = get_user_model()

class UserSignupTests(APITestCase):
    """
    Test suite for user signup functionality.
    Classes:
        UserSignupTests: Test cases for user signup API endpoint.
    Methods:
        setUp(self):
            Sets up the test environment by defining the signup URL and user data.
        test_signup_success(self):
            Tests that a user can successfully sign up with valid data.
        test_signup_user_already_exists(self):
            Tests that attempting to sign up with an email that already exists returns a 400 status code.
        test_signup_invalid_data(self):
            Tests that attempting to sign up with invalid data returns a 400 status code and appropriate error message.
    """

    def setUp(self):
        self.signup_url = reverse('signup')
        self.image_path = os.path.join(os.path.dirname(__file__), 'media', 'test_1.png')
        with open(self.image_path, 'rb') as image_file:
            self.user_data = {
                'email': 'testuser@example.com',
                'password': 'testpassword123',
                'first_name': 'Test',
                'gender': 'M',
                'last_name': 'User',
                'profile_picture': SimpleUploadedFile(name='test_1.png', content=image_file.read(), content_type='image/png')
            }

    def test_signup_success(self):
        response = self.client.post(self.signup_url, self.user_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User created successfully.')
        self.assertIn('data', response.data)

    def test_signup_user_already_exists(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.signup_url, self.user_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'User already exists.')

    def test_signup_invalid_data(self):
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid-email'
        response = self.client.post(self.signup_url, invalid_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'User creation failed.')
        self.assertIn('errors', response.data)


    class UserSigninTests(APITestCase):
        """
        Test suite for user signin functionality.
        Classes:
            UserSigninTests: Test cases for user signin API endpoint.
        Methods:
            setUp(self):
                Sets up the test environment by defining the signin URL and creating a test user.
            test_signin_success(self):
                Tests that a user can successfully sign in with valid credentials.
            test_signin_invalid_credentials(self):
                Tests that attempting to sign in with invalid credentials returns a 400 status code.
            test_signin_missing_credentials(self):
                Tests that attempting to sign in without providing email or password returns a 400 status code.
        """

        def setUp(self):
            self.signin_url = reverse('signin')
            self.user = User.objects.create_user(
                email='testuser@example.com',
                password='testpassword123',
                first_name='Test',
                last_name='User'
            )
            self.valid_credentials = {
                'email': 'testuser@example.com',
                'password': 'testpassword123'
            }
            self.invalid_credentials = {
                'email': 'testuser@example.com',
                'password': 'wrongpassword'
            }

        def test_signin_success(self):
            response = self.client.post(self.signin_url, self.valid_credentials, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], 'Login successful.')
            self.assertIn('access_token', response.data)
            self.assertIn('refresh_token', response.data)

        def test_signin_invalid_credentials(self):
            response = self.client.post(self.signin_url, self.invalid_credentials, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['message'], 'Invalid credentials.')

        def test_signin_missing_credentials(self):
            response = self.client.post(self.signin_url, {}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['message'], 'Email and password are required.')


    class UserSignoutTests(APITestCase):
        """
        Test suite for user signout functionality.
        Classes:
            UserSignoutTests: Test cases for user signout API endpoint.
        Methods:
            setUp(self):
                Sets up the test environment by defining the signout URL and creating a test user.
            test_signout_success(self):
                Tests that a user can successfully sign out with a valid refresh token.
            test_signout_missing_refresh_token(self):
                Tests that attempting to sign out without providing a refresh token returns a 400 status code.
            test_signout_invalid_refresh_token(self):
                Tests that attempting to sign out with an invalid refresh token returns a 400 status code.
        """

        def setUp(self):
            self.signout_url = reverse('signout')
            self.user = User.objects.create_user(
                email='testuser@example.com',
                password='testpassword123',
                first_name='Test',
                last_name='User'
            )
            self.client.force_authenticate(user=self.user)
            self.refresh_token = str(RefreshToken.for_user(self.user))

        def test_signout_success(self):
            response = self.client.post(self.signout_url, {'refresh_token': self.refresh_token}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], 'Logout successful.')

        def test_signout_missing_refresh_token(self):
            response = self.client.post(self.signout_url, {}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['message'], 'Refresh token is required.')

        def test_signout_invalid_refresh_token(self):
            response = self.client.post(self.signout_url, {'refresh_token': 'invalidtoken'}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data['message'], 'Error logging out.')
