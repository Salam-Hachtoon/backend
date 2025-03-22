import logging, os
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Create a utility logger
logger = logging.getLogger('utility_functions')
# Create un emails logger
email_logger = logging.getLogger('emails')


def generate_jwt_tokens(user):
    """
    Generate JWT access and refresh tokens for a given user.
    Args:
        user (User): The user instance for whom the tokens are being generated.
    Returns:
        tuple: A tuple containing the access token (str) and the refresh token (str).
    """
    
    refresh = RefreshToken.for_user(user)

    # You can customize the expiration time here if needed
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    return access_token, refresh_token


def send_email_with_attachments(subject, template_name, context, recipient_list, attachments=None):
    """
    Sends an email with both plain text and HTML content, and optional attachments.
    Args:
        subject (str): The subject of the email.
        template_name (str): The base name of the email templates (without extension).
        context (dict): A dictionary containing context variables to render the templates.
        recipient_list (list): A list of recipient email addresses.
        attachments (list, optional): A list of file paths to attach to the email. Defaults to None.
    Returns:
        str: A success message if the email is sent successfully, otherwise an error message.
    """
    # The html and the txt file should have the same name
    try:
        # Load HTML template
        emails_dir = os.path.join(settings.BASE_DIR, "users/emails")
        html_template_path = os.path.join(emails_dir, "templates", "{}.html".format(template_name))
        html_content = render_to_string(html_template_path, context)

        # Load plain text template
        txt_template_path = os.path.join(emails_dir, "plain_text", "{}.txt".format(template_name))
        with open(txt_template_path, "r", encoding="utf-8") as file:
            plain_text_content = file.read().format(**context)  # Replace placeholders with context values

        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_text_content,  # Plain text version
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")  # Attach HTML version

        # Attach files if provided
        if attachments:
            for attachment in attachments:
                email.attach_file(attachment)

        email.send(fail_silently=False)
        logger.info("Email sent successfully!")

    except Exception as e:
        email_logger.error("Error sending email: {}".format(str(e)))
