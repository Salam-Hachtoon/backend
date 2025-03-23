import os, time
from django.urls import reverse
from rest_framework.test import APITestCase # type: ignore
from rest_framework import status # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from ..models import Attachment, Summary, FlashCard, Quiz, Bookmark
from users.models import User
from unittest.mock import patch
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from ..models import Attachment


class AiAssistantViewsTests(APITestCase):
    """
    Unit tests for the AI Assistant views.
    This test suite includes the following test cases:
    1. `test_upload_attachments_success`: Tests the successful upload of attachments.
    2. `test_get_summary_success`: Tests the successful generation of a summary using the AI service.
    3. `test_get_flash_cards_success`: Tests the successful generation of flashcards from a summary using the AI service.
    4. `test_get_quiz_success`: Tests the successful generation of a quiz from a summary using the AI service.
    5. `test_create_bookmark_success`: Tests the successful creation of a bookmark for a summary.
    6. `test_get_user_summaries`: Tests retrieving all summaries created by the user.
    7. `test_get_user_flashcards`: Tests retrieving all flashcards associated with the user's summaries.
    8. `test_get_user_quizzes`: Tests retrieving all quizzes associated with the user's summaries.
    9. `test_get_user_attachments`: Tests retrieving all attachments uploaded by the user.
    10. `test_check_attachments_success_all_processed`: Tests checking the status of attachments when all files are processed.
    11. `test_check_attachments_success_some_unprocessed`: Tests checking the status of attachments when some files are still unprocessed.
    12. `test_check_attachments_no_files_found`: Tests checking the status of attachments when no files are found for the given batch ID.
    13. `test_check_attachments_missing_batch_id`: Tests checking the status of attachments when the batch ID is not provided.
    Each test case ensures that the corresponding view behaves as expected under various conditions.
    """
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)

        # Generate JWT tokens
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh_token.access_token)

        # URLs for the views
        self.upload_attachments_url = reverse('upload_attachments')  # Replace with actual URL name
        self.get_summary_url = reverse('get_summary')  # Replace with actual URL name
        self.get_flash_cards_url = reverse('get_flash_cards')  # Replace with actual URL name
        self.get_quiz_url = reverse('get_quiz')  # Replace with actual URL name
        self.create_bookmark_url = reverse('create_bookmark')  # Replace with actual URL name
        self.get_user_summaries_url = reverse('get_user_summaries')  # Replace with actual URL name
        self.get_user_flashcards_url = reverse('get_user_flashcards')  # Replace with actual URL name
        self.get_user_quizzes_url = reverse('get_user_quizzes')  # Replace with actual URL name
        self.get_user_attachments_url = reverse('get_user_attachments')  # Replace with actual URL name

    def test_upload_attachments_success(self):
        self.file_path = os.path.join(os.path.dirname(__file__), 'attachments', 'test_1.pdf')
        with open(self.file_path, 'rb') as file:
            files = [
                SimpleUploadedFile(name='test_1.pdf', content=file.read(), content_type='application/pdf'),
                SimpleUploadedFile(name='test_2.pdf', content=file.read(), content_type='application/pdf')
            ]
            response = self.client.post(self.upload_attachments_url, {'files': files}, format='multipart')
            time.sleep(10)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['message'], 'Files uploaded successfully.')
            self.assertTrue(Attachment.objects.filter(user=self.user).exists())

    def test_get_summary_success(self):
        # Mock the AI service response
        with patch('ai_assistant.views.call_deepseek_ai_summary') as mock_ai_summary:
            mock_ai_summary.return_value = '{"summary": {"content": "This is a test summary."}}'

            # Create attachments for the batch
            batch_id = '12345'
            Attachment.objects.create(user=self.user, file='file1.pdf', batch_id=batch_id, status='completed')
            
            response = self.client.post(self.get_summary_url, {'batch_id': batch_id})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['message'], 'Summary created successfully.')
            self.assertTrue(Summary.objects.filter(user=self.user).exists())

    def test_get_flash_cards_success(self):
        # Mock the AI service response
        with patch('ai_assistant.views.call_deepseek_ai_flashcards') as mock_ai_flashcards:
            mock_ai_flashcards.return_value = '{"flashcards": [{"term": "Test Term", "definition": "Test Definition"}]}'

            # Create a summary
            summary = Summary.objects.create(user=self.user, content='Test summary content')

            response = self.client.post(self.get_flash_cards_url, {'id': summary.id})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['message'], 'Flashcards generated and saved successfully.')
            self.assertTrue(FlashCard.objects.filter(summary=summary).exists())

    def test_get_quiz_success(self):
        # Mock the AI service response
        with patch('ai_assistant.views.call_deepseek_ai_quizes') as mock_ai_quizes:
            mock_ai_quizes.return_value = '{"quiz": {"difficulty": "easy", "questions": [{"question_text": "What is Django?", "choices": ["A framework", "A language"], "correct_answer": "A framework"}]}}'

            # Create a summary
            summary = Summary.objects.create(user=self.user, content='Test summary content')

            response = self.client.post(self.get_quiz_url, {'id': summary.id, 'difficulty': 'easy'})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['message'], 'Quiz generated and saved successfully.')
            self.assertTrue(Quiz.objects.filter(summary=summary).exists())

    def test_create_bookmark_success(self):
        # Create a summary to bookmark
        summary = Summary.objects.create(user=self.user, content='Test summary content')
        content_type = ContentType.objects.get_for_model(Summary)

        response = self.client.post(self.create_bookmark_url, {'object_id': summary.id, 'model_name': 'summary'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], f"Bookmark created successfully for summary with ID {summary.id}.")
        self.assertTrue(Bookmark.objects.filter(user=self.user, content_type=content_type, object_id=summary.id).exists())

    def test_get_user_summaries(self):
        # Create summaries for the user
        Summary.objects.create(user=self.user, content='Summary 1')
        Summary.objects.create(user=self.user, content='Summary 2')

        response = self.client.get(self.get_user_summaries_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User summaries retrieved successfully.')
        self.assertEqual(len(response.data['data']), 2)

    def test_get_user_flashcards(self):
        # Create a summary and flashcards for the user
        summary = Summary.objects.create(user=self.user, content='Test summary content')
        FlashCard.objects.create(summary=summary, term='Term 1', definition='Definition 1')
        FlashCard.objects.create(summary=summary, term='Term 2', definition='Definition 2')

        response = self.client.get(self.get_user_flashcards_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User flashcards retrieved successfully.')
        self.assertEqual(len(response.data['data']), 2)

    def test_get_user_quizzes(self):
        # Create quizzes for the user
        Quiz.objects.create(user=self.user, summary=Summary.objects.create(user=self.user, content='Test summary'), difficulty='easy')
        Quiz.objects.create(user=self.user, summary=Summary.objects.create(user=self.user, content='Another summary'), difficulty='medium')

        response = self.client.get(self.get_user_quizzes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User quizzes retrieved successfully.')
        self.assertEqual(len(response.data['data']), 2)

    def test_get_user_attachments(self):
        # Create attachments for the user
        Attachment.objects.create(user=self.user, file='file1.txt', batch_id='12345', status='completed')
        Attachment.objects.create(user=self.user, file='file2.txt', batch_id='12345', status='completed')

        response = self.client.get(self.get_user_attachments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User attachments retrieved successfully.')
        self.assertEqual(len(response.data['data']), 2)

    def test_check_attachments_success_all_processed(self):
        # Create attachments for the batch
        batch_id = '12345'
        Attachment.objects.create(user=self.user, file='file1.pdf', batch_id=batch_id, status='completed')
        Attachment.objects.create(user=self.user, file='file2.pdf', batch_id=batch_id, status='completed')

        response = self.client.post(reverse('check_attachments'), {'batch_id': batch_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'All files have been processed.')
        self.assertEqual(len(response.data['processed_files']), 2)

    def test_check_attachments_success_some_unprocessed(self):
        # Create attachments for the batch
        batch_id = '12345'
        Attachment.objects.create(user=self.user, file='file1.pdf', batch_id=batch_id, status='completed')
        Attachment.objects.create(user=self.user, file='file2.pdf', batch_id=batch_id, status='pending')

        response = self.client.post(reverse('check_attachments'), {'batch_id': batch_id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Not all files have been processed yet.')
        self.assertEqual(len(response.data['unprocessed_files']), 1)

    def test_check_attachments_no_files_found(self):
        # Use a batch ID that does not exist
        batch_id = 'nonexistent_batch'

        response = self.client.post(reverse('check_attachments'), {'batch_id': batch_id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], f'No files found for batch ID: {batch_id}')

    def test_check_attachments_missing_batch_id(self):
        response = self.client.post(reverse('check_attachments'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Batch ID not provided.')


