from django.urls import reverse
from rest_framework.test import APITestCase # type: ignore
from rest_framework import status # type: ignore
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from ..models import Attachment
from users.models import User



class UploadAttachmentsTests(APITestCase):
    """
    Test suite for the `upload_attachments` API endpoint.
    This test class contains unit tests to verify the functionality of the
    `upload_attachments` endpoint, including successful file uploads, handling
    of invalid data, and authentication requirements.
    Test Cases:
    - `test_upload_attachments_success`: Verifies that valid files are uploaded
        successfully, and the appropriate response is returned.
    - `test_upload_attachments_invalid_data`: Ensures that invalid file data
        results in a 400 Bad Request response with error details.
    - `test_upload_attachments_unauthenticated`: Confirms that unauthenticated
        requests to the endpoint are denied with a 401 Unauthorized response.
    Setup:
    - Creates a test user and authenticates the client.
    - Defines valid and invalid file data for testing.
    """

    def setUp(self):
        self.upload_attachments_url = reverse('upload_attachments')  # Replace with the actual URL name
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        self.valid_files = [
            SimpleUploadedFile(name='file1.txt', content=b'Test content 1', content_type='text/plain'),
            SimpleUploadedFile(name='file2.txt', content=b'Test content 2', content_type='text/plain')
        ]
        self.invalid_files = [
            SimpleUploadedFile(name='file1.txt', content=b'', content_type='text/plain')  # Empty file
        ]

    def test_upload_attachments_success(self):
        data = {'files': self.valid_files}
        response = self.client.post(self.upload_attachments_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Files uploaded successfully.')
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), len(self.valid_files))
        self.assertTrue(Attachment.objects.filter(user=self.user).exists())

    def test_upload_attachments_invalid_data(self):
        data = {'files': self.invalid_files}
        response = self.client.post(self.upload_attachments_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid file upload data.')
        self.assertIn('errors', response.data)

    def test_upload_attachments_unauthenticated(self):
        self.client.force_authenticate(user=None)  # Unauthenticate the client
        data = {'files': self.valid_files}
        response = self.client.post(self.upload_attachments_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
