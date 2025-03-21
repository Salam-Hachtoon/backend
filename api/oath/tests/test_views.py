
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from ...users.models import User


class GoogleOAuthTests(APITestCase):
    """
    Test suite for Google OAuth views.
    This test class contains unit tests to verify the functionality of the
    `google_login` and `google_callback` views.
    """

    def setUp(self):
        self.google_login_url = reverse('google_login')  # Replace with the actual URL name
        self.google_callback_url = reverse('google_callback')  # Replace with the actual URL name
        self.user_data = {
            "email": "testuser@example.com",
            "given_name": "Test",
            "family_name": "User",
            "picture": "http://example.com/profile.jpg"
        }

    def test_google_login_redirect(self):
        """
        Test that the `google_login` view redirects to the Google OAuth URL.
        """
        response = self.client.get(self.google_login_url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("https://accounts.google.com/o/oauth2/auth", response.url)

    @patch("api.oath.views.requests.post")
    @patch("api.oath.views.requests.get")
    def test_google_callback_success(self, mock_get, mock_post):
        """
        Test that the `google_callback` view successfully exchanges the code
        for an access token and retrieves user info.
        """
        # Mock the token response
        mock_post.return_value.json.return_value = {"access_token": "mock_access_token"}

        # Mock the user info response
        mock_get.return_value.json.return_value = self.user_data

        # Simulate the callback request with a valid code
        response = self.client.get(self.google_callback_url, {"code": "mock_code"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Login successful")
        self.assertEqual(response.data["user"]["email"], self.user_data["email"])
        self.assertEqual(response.data["user"]["first_name"], self.user_data["given_name"])
        self.assertEqual(response.data["user"]["last_name"], self.user_data["family_name"])
        self.assertEqual(response.data["user"]["profile_picture"], self.user_data["picture"])

        # Verify that the user was created in the database
        user = User.objects.get(email=self.user_data["email"])
        self.assertEqual(user.first_name, self.user_data["given_name"])
        self.assertEqual(user.last_name, self.user_data["family_name"])

    def test_google_callback_no_code(self):
        """
        Test that the `google_callback` view returns an error if no code is provided.
        """
        response = self.client.get(self.google_callback_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "No code provided")

    @patch("api.oath.views.requests.post")
    def test_google_callback_failed_token_exchange(self, mock_post):
        """
        Test that the `google_callback` view returns an error if the token exchange fails.
        """
        # Mock a failed token response
        mock_post.return_value.json.return_value = {}

        response = self.client.get(self.google_callback_url, {"code": "mock_code"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Failed to obtain access token")

    @patch("api.oath.views.requests.post")
    @patch("api.oath.views.requests.get")
    def test_google_callback_failed_user_info(self, mock_get, mock_post):
        """
        Test that the `google_callback` view returns an error if user info retrieval fails.
        """
        # Mock the token response
        mock_post.return_value.json.return_value = {"access_token": "mock_access_token"}

        # Mock a failed user info response
        mock_get.return_value.json.return_value = {}

        response = self.client.get(self.google_callback_url, {"code": "mock_code"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Failed to retrieve email")

