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
        self.assertIn('refresh_token', response.cookies)

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


class UserInfoTests(APITestCase):
    """
    Test suite for user info retrieval functionality.
    Classes:
        UserInfoTests: Test cases for user info API endpoint.
    Methods:
        setUp(self):
            Sets up the test environment by defining the userinfo URL and creating a test user.
        test_userinfo_success(self):
            Tests that user information can be successfully retrieved with a valid refresh token.
        test_userinfo_missing_refresh_token(self):
            Tests that attempting to retrieve user info without providing a refresh token returns a 400 status code.
        test_userinfo_invalid_refresh_token(self):
            Tests that attempting to retrieve user info with an invalid refresh token returns a 400 status code.
    """

    def setUp(self):
        self.userinfo_url = reverse('userinfo')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_userinfo_success(self):
        response = self.client.post(self.userinfo_url, {'refresh_token': self.refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User info retrieved successfully.')
        self.assertIn('data', response.data)

    def test_userinfo_missing_refresh_token(self):
        response = self.client.post(self.userinfo_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Refresh token is required.')

    def test_userinfo_invalid_refresh_token(self):
        response = self.client.post(self.userinfo_url, {'refresh_token': 'invalidtoken'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Error retrieving user info.')


class RefreshTokenTests(APITestCase):
    """
    Tests for the refresh token functionality in the API.

    Classes:
        RefreshTokenTests: Test case for testing the refresh token endpoint.

    Methods:
        setUp(self):
            Sets up the test environment, including creating a user and generating a refresh token.

        test_refresh_token_success(self):
            Tests that a valid refresh token in cookies generates a new access token successfully.

        test_refresh_token_missing(self):
            Tests that a missing refresh token in the request results in a 400 Bad Request response.

        test_refresh_token_invalid(self):
            Tests that an invalid refresh token in cookies results in a 400 Bad Request response.
    """

    def setUp(self):
        self.refresh_token_url = reverse('refresh_token')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_refresh_token_success(self):
        self.client.cookies['refresh_token'] = self.refresh_token  # Set the refresh token in cookies
        response = self.client.post(self.refresh_token_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Access token generated successfully.')
        self.assertIn('access_token', response.data)

    def test_refresh_token_missing(self):
        response = self.client.post(self.refresh_token_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Refresh token is required.')

    def test_refresh_token_invalid(self):
        self.client.cookies['refresh_token'] = 'invalidtoken'  # Set an invalid refresh token in cookies
        response = self.client.post(self.refresh_token_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid refresh token.')


class UpdateAccountTests(APITestCase):
    """
    Test suite for updating user account information.
    Classes:
        UpdateAccountTests: Test cases for the update account API endpoint.
    Methods:
        setUp(self):
            Sets up the test environment by defining the update account URL and creating a test user.
        test_update_account_success(self):
            Tests that a user can successfully update their account information with valid data.
        test_update_account_invalid_data(self):
            Tests that attempting to update account information with invalid data returns a 400 status code.
        test_update_account_partial_update(self):
            Tests that a user can successfully update partial account information.
        test_update_account_profile_picture(self):
            Tests that a user can successfully update their profile picture.
    """

    def setUp(self):
        self.update_account_url = reverse('update_account')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        self.valid_data = {
            'first_name': 'UpdatedTest',
            'last_name': 'UpdatedUser',
            'password': 'updatedpassword123'
        }
        self.invalid_data = {
            'email': 'invalid-email'
        }
        self.partial_data = {
            'first_name': 'PartialUpdate'
        }
        self.image_path = os.path.join(os.path.dirname(__file__), 'media', 'test_1.png')
        with open(self.image_path, 'rb') as image_file:
            self.profile_picture_data = {
                'profile_picture': SimpleUploadedFile(name='test_1.png', content=image_file.read(), content_type='image/png')
            }

    def test_update_account_success(self):
        response = self.client.put(self.update_account_url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User updated successfully.')
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['first_name'], 'UpdatedTest')
        self.assertEqual(response.data['data']['last_name'], 'UpdatedUser')

    def test_update_account_invalid_data(self):
        response = self.client.put(self.update_account_url, self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'User update failed.')
        self.assertIn('errors', response.data)

    def test_update_account_partial_update(self):
        response = self.client.put(self.update_account_url, self.partial_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User updated successfully.')
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['first_name'], 'PartialUpdate')

    def test_update_account_profile_picture(self):
        response = self.client.put(self.update_account_url, self.profile_picture_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User updated successfully.')
        self.assertIn('data', response.data)
        self.assertTrue('profile_picture' in response.data['data'])


class ChangePasswordTests(APITestCase):
    """
    Test suite for change password functionality.
    Classes:
        ChangePasswordTests: Test cases for change password API endpoint.
    Methods:
        setUp(self):
            Sets up the test environment by defining the change password URL and creating a test user.
        test_change_password_success(self):
            Tests that an OTP code is generated and sent to the user's email if the email exists.
        test_change_password_missing_email(self):
            Tests that attempting to change password without providing an email returns a 200 status code with a generic message.
        test_change_password_user_not_found(self):
            Tests that attempting to change password with a non-existent email returns a 200 status code with a generic message.
    """

    def setUp(self):
        self.change_password_url = reverse('change_password')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        self.valid_email = {'email': 'testuser@example.com'}
        self.invalid_email = {'email': 'nonexistent@example.com'}

    def test_change_password_success(self):
        with self.assertLogs('info', level='INFO') as cm:
            response = self.client.post(self.change_password_url, self.valid_email, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], 'If an account with this email exists, a password reset link will be sent.')
            self.assertIn('message', response.data)
            self.assertIn('Password Reset Request - Your OTP Code', cm.output[0])

    def test_change_password_missing_email(self):
        response = self.client.post(self.change_password_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'If an account with this email exists, a password reset link will be sent.')

    def test_change_password_user_not_found(self):
        response = self.client.post(self.change_password_url, self.invalid_email, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'If an account with this email exists, a password reset link will be sent.')

class VerifyOtpTests(APITestCase):
    """
    Test suite for OTP verification functionality.
    Classes:
        VerifyOtpTests: Test cases for OTP verification API endpoint.
    Methods:
        setUp(self):
            Sets up the test environment by defining the verify OTP URL and creating a test user.
        test_verify_otp_success(self):
            Tests that a user can successfully verify OTP and receive JWT tokens.
        test_verify_otp_missing_data(self):
            Tests that attempting to verify OTP without providing email or OTP code returns a 400 status code.
        test_verify_otp_invalid_otp(self):
            Tests that attempting to verify OTP with an invalid OTP code returns a 400 status code.
        test_verify_otp_user_not_found(self):
            Tests that attempting to verify OTP with a non-existent email returns a 404 status code.
    """

    def setUp(self):
        self.verify_otp_url = reverse('verfy_otp')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        self.valid_data = {
            'email': 'testuser@example.com',
            'otp_code': '123456'  # Assuming this is the valid OTP code
        }
        self.invalid_otp_data = {
            'email': 'testuser@example.com',
            'otp_code': '654321'
        }
        self.missing_data = {
            'email': 'testuser@example.com'
        }
        self.non_existent_user_data = {
            'email': 'nonexistent@example.com',
            'otp_code': '123456'
        }
    # Need to check the emails output
    # def test_verify_otp_success(self):
    #     self.user.generate_otp = lambda: '123456'  # Mock the OTP generation
    #     self.user.save()
    #     response = self.client.post(self.verify_otp_url, self.valid_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['message'], 'Login successful.')
    #     self.assertIn('access_token', response.data)
    #     self.assertIn('refresh_token', response.cookies)

    # def test_verify_otp_missing_data(self):
    #     response = self.client.post(self.verify_otp_url, self.missing_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data['message'], 'Email and OTP code are required.')

    # def test_verify_otp_invalid_otp(self):
    #     self.user.generate_otp = lambda: '123456'  # Mock the OTP generation
    #     self.user.save()
    #     response = self.client.post(self.verify_otp_url, self.invalid_otp_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data['message'], 'Invalid OTP code.')

    # def test_verify_otp_user_not_found(self):
    #     response = self.client.post(self.verify_otp_url, self.non_existent_user_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #     self.assertEqual(response.data['message'], 'User not found.')

