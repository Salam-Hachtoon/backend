import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from unittest.mock import patch, mock_open
from django.test import TestCase
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from user.utility import send_email_with_attachments
from .models import User

class UserRegistrationTest(APITestCase):
    """
    Test case for user registration.
    This test case verifies that a user can successfully register by sending a POST request
    to the registration endpoint with the required user details. It checks that the response
    status code is 201 (Created), the response message indicates successful user creation,
    and that the user is actually created in the database.
    Methods:
        test_register_user: Tests user registration functionality.
    """
    
    def test_register_user(self):
        url = reverse('register')  # Ensure this matches your URL name
        data = {
            "email": "johndoe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User created successfully.')
        self.assertTrue(User.objects.filter(email="johndoe@example.com").exists())


class UserLoginTest(APITestCase):
    """
    Tests for user login functionality.
    Classes:
        UserLoginTest: Test case for user login.
    Methods:
        setUp(self): Sets up a test user for login tests.
        test_login_user(self): Tests that a user can log in with valid credentials.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="johndoe@example.com",
            first_name="John",
            last_name="Doe",
            password="securepassword123"
        )

    def test_login_user(self):
        url = reverse('login')  # Ensure this matches your URL name
        data = {
            "email": "johndoe@example.com",
            "password": "securepassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Login successful.')
        self.assertIn('access_token', response.data)


class LogoutViewTests(APITestCase):
    """
    Tests for the LogoutView.
    This test case includes the following tests:
    - test_logout_successful: Ensures that a user can successfully log out with a valid refresh token.
    - test_logout_no_refresh_token: Ensures that the logout fails if no refresh token is provided.
    - test_logout_invalid_refresh_token: Ensures that the logout fails if an invalid or expired refresh token is provided.
    Setup:
    - Creates a test user.
    - Generates a refresh token and an access token for the test user.
    - Defines the logout URL.
    Tests:
    - test_logout_successful: Sends a POST request to the logout URL with a valid refresh token and checks for a 200 OK response and a success message.
    - test_logout_no_refresh_token: Sends a POST request to the logout URL without a refresh token and checks for a 400 Bad Request response and an error message.
    - test_logout_invalid_refresh_token: Sends a POST request to the logout URL with an invalid refresh token and checks for a 400 Bad Request response and an error message.
    """

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')
        self.refresh_token = str(RefreshToken.for_user(self.user))
        self.access_token = str(RefreshToken.for_user(self.user).access_token)
        self.logout_url = reverse('logout')  # Ensure you have a URL pattern named 'logout'

    def test_logout_successful(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.logout_url, {'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout successful.')

    def test_logout_no_refresh_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Refresh token not provided.')

    def test_logout_invalid_refresh_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.logout_url, {'refresh_token': 'invalidtoken'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid or expired refresh token.')


class SendEmailWithAttachmentsTest(TestCase):
    """
    Unit tests for the send_email_with_attachments function.
    Classes:
        SendEmailWithAttachmentsTest: Test case for sending emails with and without attachments.
    Methods:
        test_send_email_success: Tests successful email sending with attachments.
        test_send_email_without_attachments: Tests successful email sending without attachments.
        test_send_email_failure: Tests email sending failure scenario.
    """
    
    @patch('user.utility.render_to_string')
    @patch('builtins.open', new_callable=mock_open, read_data="Plain text content with {placeholder}")
    @patch('user.utility.EmailMultiAlternatives')
    def test_send_email_success(self, mock_email, mock_open, mock_render_to_string):
        mock_render_to_string.return_value = "<html>HTML content with value</html>"
        mock_email_instance = mock_email.return_value

        subject = "Test Subject"
        template_name = "test_template"
        context = {"placeholder": "value"}
        recipient_list = ["test@example.com"]

        send_email_with_attachments(subject, template_name, context, recipient_list)

        expected_template_path = os.path.join(settings.BASE_DIR, "user/emails/templates/{}.html".format(template_name))
        mock_render_to_string.assert_called_once_with(expected_template_path, context)
        mock_email_instance.attach_alternative.assert_called_once_with("<html>HTML content with value</html>", "text/html")
        mock_email_instance.send.assert_called_once()

    @patch('user.utility.render_to_string')
    @patch('builtins.open', new_callable=mock_open, read_data="Plain text content with {placeholder}")
    @patch('user.utility.EmailMultiAlternatives')
    def test_send_email_without_attachments(self, mock_email, mock_open, mock_render_to_string):
        mock_render_to_string.return_value = "<html>HTML content with value</html>"
        mock_email_instance = mock_email.return_value

        subject = "Test Subject"
        template_name = "test_template"
        context = {"placeholder": "value"}
        recipient_list = ["test@example.com"]

        send_email_with_attachments(subject, template_name, context, recipient_list)

        expected_template_path = os.path.join(settings.BASE_DIR, "user/emails/templates/{}.html".format(template_name))
        mock_render_to_string.assert_called_once_with(expected_template_path, context)
        mock_email_instance.attach_alternative.assert_called_once_with("<html>HTML content with value</html>", "text/html")
        mock_email_instance.send.assert_called_once()

    @patch('user.utility.render_to_string')
    @patch('builtins.open', new_callable=mock_open, read_data="Plain text content with {placeholder}")
    @patch('user.utility.EmailMultiAlternatives')
    def test_send_email_failure(self, mock_email, mock_open, mock_render_to_string):
        mock_render_to_string.return_value = "<html>HTML content with value</html>"
        mock_email_instance = mock_email.return_value

        subject = "Test Subject"
        template_name = "test_template"
        context = {"placeholder": "value"}
        recipient_list = ["test@example.com"]

        send_email_with_attachments(subject, template_name, context, recipient_list)

        expected_template_path = os.path.join(settings.BASE_DIR, "user/emails/templates/{}.html".format(template_name))
        mock_render_to_string.assert_called_once_with(expected_template_path, context)
        mock_email_instance.attach_alternative.assert_called_once_with("<html>HTML content with value</html>", "text/html")
        mock_email_instance.send.assert_called_once()


class UpdateUserProfileTests(APITestCase):
    """
    Tests for updating user profile functionality.
    Classes:
        UpdateUserProfileTests: Test case for updating user profile.
    Methods:
        setUp(self):
            Set up the test case with a test user and authenticate the client.
        test_updateUserProfile(self):
            Test updating user profile with valid data including profile picture.
        test_updateUserProfile_with_invalid_data(self):
            Test updating user profile with invalid data (empty first and last name).
        test_update_profile_image_size_exceeds_limit(self):
            Test updating user profile with an image that exceeds the size limit (5MB).
        test_update_profile_invalid_image_extension(self):
            Test updating user profile with an invalid image file extension.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('updateUserProfile')

    def test_updateUserProfile(self):
        with open(os.path.join(settings.BASE_DIR, 'media/profile_pics/1_pYBLqLl57uiXHFSWYEzOlw_B5AlHJt.png'), 'rb') as f:
            image = SimpleUploadedFile('1_pYBLqLl57uiXHFSWYEzOlw_B5AlHJt.png', f.read(), content_type='image/png')
            data = {
                'first_name': 'Updated',
                'last_name': 'User',
                'profile_picture': image
            }
            response = self.client.put(self.url, data, format='multipart')  # Use multipart for file upload            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], 'Profile updated successfully')

    def test_updateUserProfile_with_invalid_data(self):
        data = {
            'first_name': '',
            'last_name': ''
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_image_size_exceeds_limit(self):
        with open('large_image.jpg', 'wb') as f:
            f.write(b'\x00' * (5 * 1024 * 1024 + 1))  # Create a file larger than 5MB
        with open('large_image.jpg', 'rb') as f:
            image = SimpleUploadedFile('large_image.jpg', f.read(), content_type='image/jpeg')
            data = {
                'first_name': 'Updated',
                'last_name': 'User',
                'profile_picture': image
            }
            response = self.client.put(self.url, data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('Upload a valid image. The file you uploaded was either not an image or a corrupted image.', response.data['errors']['profile_picture'][0])

    def test_update_profile_invalid_image_extension(self):
        with open('invalid_image.txt', 'wb') as f:
            f.write(b'This is not an image file.')
        with open('invalid_image.txt', 'rb') as f:
            image = SimpleUploadedFile('invalid_image.txt', f.read(), content_type='text/plain')
            data = {
                'first_name': 'Updated',
                'last_name': 'User',
                'profile_picture': image
            }
            response = self.client.put(self.url, data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('Upload a valid image. The file you uploaded was either not an image or a corrupted image.', response.data['errors']['profile_picture'][0])
