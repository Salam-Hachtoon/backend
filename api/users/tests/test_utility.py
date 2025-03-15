import hashlib, os
from django.test import TestCase
from unittest.mock import patch, mock_open
from ..utility import send_email_with_attachments
from django.conf import settings


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
