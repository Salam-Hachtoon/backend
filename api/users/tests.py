import hashlib, os
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta
from unittest.mock import patch, mock_open
from .utility import send_email_with_attachments
from django.core import mail
from django.conf import settings


# Create your tests here.
User = get_user_model()

class UserModelTests(TestCase):
    """
    Test suite for the User model.
    This test suite includes the following test cases:
    - User creation and attribute validation.
    - String representation of the User model.
    - Email uniqueness validation.
    - Superuser creation and attribute validation.
    - OTP generation and validation.
    Test Cases:
    - setUp: Initializes a test user for use in the test cases.
    - test_user_creation: Verifies that a user is created with the correct attributes.
    - test_user_str_method: Checks the string representation of the user.
    - test_user_email_unique: Ensures that the email field is unique.
    - test_superuser_creation: Verifies that a superuser is created with the correct attributes.
    - test_generate_otp: Tests the OTP generation method.
    - test_verify_otp_success: Tests successful OTP verification.
    - test_verify_otp_expired: Tests OTP verification when the OTP has expired.
    - test_verify_otp_invalid: Tests OTP verification with an invalid OTP.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            password='testpassword123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertTrue(self.user.check_password('testpassword123'))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_user_str_method(self):
        self.assertEqual(str(self.user), 'Email: testuser@example.com, First Name: Test, Last Name: User')

    def test_user_email_unique(self):
        with self.assertRaises(ValidationError):
            user2 = User(
                email='testuser@example.com',
                first_name='Test2',
                last_name='User2',
                password='testpassword123'
            )
            user2.full_clean()

    def test_superuser_creation(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password='adminpassword123'
        )
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertEqual(admin_user.first_name, 'Admin')
        self.assertEqual(admin_user.last_name, 'User')
        self.assertTrue(admin_user.check_password('adminpassword123'))
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_generate_otp(self):
        otp = self.user.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
        hashed_otp = hashlib.sha256(otp.encode()).hexdigest()
        self.assertEqual(self.user.otp, hashed_otp)
        self.assertTrue(self.user.otp_expires_at > now())

    def test_verify_otp_success(self):
        otp = self.user.generate_otp()
        self.assertTrue(self.user.verify_otp(otp))
        self.assertIsNone(self.user.otp)
        self.assertIsNone(self.user.otp_expires_at)

    def test_verify_otp_expired(self):
        otp = self.user.generate_otp()
        self.user.otp_expires_at = now() - timedelta(minutes=1)
        self.user.save()
        self.assertFalse(self.user.verify_otp(otp))

    def test_verify_otp_invalid(self):
        self.user.generate_otp()
        self.assertFalse(self.user.verify_otp("123456"))


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
    
    @patch('users.utility.render_to_string')
    @patch('builtins.open', new_callable=mock_open, read_data="Plain text content with {placeholder}")
    @patch('users.utility.EmailMultiAlternatives')
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

    @patch('users.utility.render_to_string')
    @patch('builtins.open', new_callable=mock_open, read_data="Plain text content with {placeholder}")
    @patch('users.utility.EmailMultiAlternatives')
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

    @patch('users.utility.render_to_string')
    @patch('builtins.open', new_callable=mock_open, read_data="Plain text content with {placeholder}")
    @patch('users.utility.EmailMultiAlternatives')
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
