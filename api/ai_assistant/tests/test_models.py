from ..models import Attachment, Summary, FlashCard, Quiz, Question, Choice
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model
import os
from django.conf import settings


User = get_user_model()



class AttachmentModelTests(TestCase):
    """
    Test suite for the Attachment model.
    This test case ensures the proper functionality of the Attachment model, including
    its creation, field values, and string representation.
    Methods:
        setUp():
            Sets up the test environment by creating a user and an attachment instance.
        test_attachment_creation():
            Verifies that the attachment instance is created with the correct user, file,
            status, and that the `uploaded_at` field is not None.
        test_attachment_str_method():
            Tests the string representation of the attachment instance to ensure it matches
            the expected format.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.file_path = os.path.join(os.path.dirname(__file__), 'attachments', 'test_1.pdf')
        with open(self.file_path, 'rb') as file:
            self.attachment = Attachment.objects.create(
                user=self.user,
                file=SimpleUploadedFile(name='test_1.pdf', content=file.read(), content_type='application/pdf'),
                extracted_text="Extracted text content",
                status="completed"
            )

    def test_attachment_creation(self):
        self.assertEqual(self.attachment.user, self.user)
        self.assertTrue(self.attachment.file.name.startswith("attachments/"))
        self.assertTrue(self.attachment.file.name.endswith(".pdf"))
        self.assertEqual(self.attachment.extracted_text, "Hiba Hanafi Mohamed 30/07/2024 *Earners of this badge have completed the McKinsey Forward online learning program. This program enables participants to develop practical skills for success in the future of work. Participants learn how to apply the McKinsey approach to problem- solving, become more effective and influential communicators and develop adaptable and resilience mindsets and habits. They also learn how to plan for and develop a foundational digital toolkit. *Please note that McKinsey is not an accredited education body, and thus participants of the Forward program will not receive an accredited qualification or credential. Powered by PDF Generator API _________________________________	")
        self.assertEqual(self.attachment.status, "completed")
        self.assertIsNotNone(self.attachment.uploaded_at)

    def test_attachment_default_status(self):
        self.file_path = os.path.join(os.path.dirname(__file__), 'attachments', 'test_1.pdf')
        with open(self.file_path, 'rb') as file:
            attachment = Attachment.objects.create(
                user=self.user,
                file=SimpleUploadedFile(name='test_1.pdf', content=file.read(), content_type='application/pdf')
            )
            self.assertEqual(attachment.status, "processing")

    def test_attachment_str_method(self):
        self.assertEqual(str(self.attachment), f"{self.user} - {self.attachment.file.name}")


class SummaryModelTests(TestCase):
    """
    Test suite for the Summary model.
    Classes:
        SummaryModelTests: Contains unit tests for the Summary model.
    Methods:
        setUp():
            Sets up the test environment by creating a test user, attachment, and summary instance.
        test_summary_creation():
            Tests the creation of a Summary instance and verifies its attributes.
        test_summary_str_method():
            Tests the string representation (__str__ method) of the Summary model.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.file_path = os.path.join(os.path.dirname(__file__), 'attachments', 'test_1.pdf')
        with open(self.file_path, 'rb') as file:
            self.attachment = Attachment.objects.create(
                user=self.user,
                file=SimpleUploadedFile(name='test_1.pdf', content=file.read(), content_type='application/pdf')
            )
            self.summary = Summary.objects.create(
                user=self.user,
                attachment=self.attachment,
                content="This is a test summary."
            )

    def test_summary_creation(self):
        self.assertEqual(self.summary.user, self.user)
        self.assertEqual(self.summary.attachment, self.attachment)
        self.assertEqual(self.summary.content, "This is a test summary.")
        self.assertIsNotNone(self.summary.created_at)

    def test_summary_str_method(self):
        self.assertEqual(str(self.summary), f"{self.user} - {self.summary.created_at}")


class FlashCardModelTests(TestCase):
    """
    Test suite for the FlashCard model.
    This test case ensures the proper functionality of the FlashCard model, 
    including its creation and string representation.
    Methods:
    - setUp: Prepares test data, including a user, a summary, and a flashcard instance.
    - test_flashcard_creation: Verifies that the flashcard is correctly associated with 
        the summary and that its term and definition are set as expected.
    - test_flashcard_str_method: Tests the string representation of the flashcard.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.summary = Summary.objects.create(
            user=self.user,
            content="This is a test summary."
        )
        self.flashcard = FlashCard.objects.create(
            summary=self.summary,
            term="Test Term",
            definition="Test Definition"
        )

    def test_flashcard_creation(self):
        self.assertEqual(self.flashcard.summary, self.summary)
        self.assertEqual(self.flashcard.term, "Test Term")
        self.assertEqual(self.flashcard.definition, "Test Definition")

    def test_flashcard_str_method(self):
        self.assertEqual(str(self.flashcard), "Test Term")


class QuizModelTests(TestCase):
    """
    Test suite for the Quiz model.
    This test case ensures the proper functionality of the Quiz model, including
    its creation, field values, and string representation.
    Methods:
        setUp():
            Sets up the test environment by creating a user, a summary, and a quiz instance.
        test_quiz_creation():
            Verifies that the quiz instance is created with the correct user, summary, difficulty,
            and that the `created_at` field is not None.
        test_quiz_str_method():
            Tests the string representation of the quiz instance to ensure it matches the expected format.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.summary = Summary.objects.create(
            user=self.user,
            content="This is a test summary."
        )
        self.quiz = Quiz.objects.create(
            user=self.user,
            summary=self.summary,
            difficulty='easy'
        )

    def test_quiz_creation(self):
        self.assertEqual(self.quiz.user, self.user)
        self.assertEqual(self.quiz.summary, self.summary)
        self.assertEqual(self.quiz.difficulty, 'easy')
        self.assertIsNotNone(self.quiz.created_at)

    def test_quiz_str_method(self):
        self.assertEqual(str(self.quiz), f"{self.quiz.id} - easy")


class QuestionModelTests(TestCase):
    """
    Test suite for the Question model.
    This test case ensures the proper creation and behavior of the Question model,
    including its relationships, fields, and string representation.
    Classes:
        QuestionModelTests: Contains unit tests for the Question model.
    Methods:
        setUp():
            Sets up the test environment by creating a user, summary, quiz, and question
            to be used in the test methods.
        test_question_creation():
            Verifies that a Question instance is correctly created with the expected
            attributes and relationships.
        test_question_str_method():
            Tests the string representation (__str__ method) of the Question model.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.summary = Summary.objects.create(
            user=self.user,
            content="This is a test summary."
        )
        self.quiz = Quiz.objects.create(
            user=self.user,
            summary=self.summary,
            difficulty='easy'
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text="What is the capital of France?",
            correct_answer="Paris"
        )

    def test_question_creation(self):
        self.assertEqual(self.question.quiz, self.quiz)
        self.assertEqual(self.question.question_text, "What is the capital of France?")
        self.assertEqual(self.question.correct_answer, "Paris")
        self.assertIsNotNone(self.question.created_at)

    def test_question_str_method(self):
        self.assertEqual(str(self.question), "What is the capital of France?")


class ChoiceModelTests(TestCase):
    """
    Tests for the Choice model.
    This test case ensures the proper creation and behavior of the Choice model,
    including its relationships with other models and its string representation.
    Test Methods:
    - setUp: Sets up the test environment by creating a user, summary, quiz, question, 
        and choice instances for use in the test methods.
    - test_choice_creation: Verifies that the Choice instance is correctly associated 
        with the Question instance, has the correct choice text, and is marked as correct.
    - test_choice_str_method: Ensures that the string representation of the Choice 
        instance matches the expected choice text.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.summary = Summary.objects.create(
            user=self.user,
            content="This is a test summary."
        )
        self.quiz = Quiz.objects.create(
            user=self.user,
            summary=self.summary,
            difficulty='easy'
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text="What is the capital of France?",
            correct_answer="Paris"
        )
        self.choice = Choice.objects.create(
            question=self.question,
            choice_text="Paris",
            is_correct=True
        )

    def test_choice_creation(self):
        self.assertEqual(self.choice.question, self.question)
        self.assertEqual(self.choice.choice_text, "Paris")
        self.assertTrue(self.choice.is_correct)

    def test_choice_str_method(self):
        self.assertEqual(str(self.choice), "Paris")
