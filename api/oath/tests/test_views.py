from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from django.conf import settings


class GoogleOAuthViewsTestCase(TestCase):
    """
    Test case for testing Google OAuth views.
    This test case includes tests for the following scenarios:
    1. Redirect behavior of the `google_login` view.
    2. Successful OAuth process in the `google_callback` view.
    3. Failed token exchange in the `google_callback` view.
    4. Missing authorization code in the `google_callback` view.
    Tested Views:
    - `google_login`: Ensures the user is redirected to the Google OAuth URL.
    - `google_callback`: Handles the callback from Google after the OAuth process.
    Mocks:
    - `requests.post`: Mocked to simulate token exchange with Google's OAuth server.
    - `requests.get`: Mocked to simulate fetching user information from Google's API.
    Test Methods:
    - `test_google_login_redirect`: Verifies the redirect to the Google OAuth URL.
    - `test_google_callback_success`: Tests the successful OAuth process, including token exchange and user info retrieval.
    - `test_google_callback_failed_token_exchange`: Tests the behavior when the token exchange fails.
    - `test_google_callback_no_code`: Tests the behavior when no authorization code is provided in the callback request.
    """

    def setUp(self):
        self.client = APIClient()
        self.google_login_url = reverse('google_login')  # Replace with the actual name of the google_login URL
        self.google_callback_url = reverse('google_callback')  # Replace with the actual name of the google_callback URL

    def test_google_login_redirect(self):
        """
        Test that the google_login view redirects to the Google OAuth URL.
        """
        response = self.client.get(self.google_login_url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("https://accounts.google.com/o/oauth2/auth", response.url)

    @patch('requests.post')
    @patch('requests.get')
    def test_google_callback_success(self, mock_get, mock_post):
        """
        Test the google_callback view when the OAuth process is successful.
        """
        # Mock the token response
        mock_post.return_value.json.return_value = {
            "access_token": "mock_access_token"
        }

        # Mock the user info response
        mock_get.return_value.json.return_value = {
            "email": "testuser@example.com",
            "given_name": "Test",
            "family_name": "User",
            "picture": "http://example.com/profile.jpg"
        }

        # Simulate the callback with a valid code
        response = self.client.get(self.google_callback_url, {'code': 'mock_code'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], "testuser@example.com")

    @patch('requests.post')
    def test_google_callback_failed_token_exchange(self, mock_post):
        """
        Test the google_callback view when the token exchange fails.
        """
        # Mock a failed token response
        mock_post.return_value.json.return_value = {}

        # Simulate the callback with an invalid code
        response = self.client.get(self.google_callback_url, {'code': 'invalid_code'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Failed to obtain access token")

    def test_google_callback_no_code(self):
        """
        Test the google_callback view when no code is provided.
        """
        response = self.client.get(self.google_callback_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "No code provided")
