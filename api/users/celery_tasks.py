import logging
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken # type: ignore
from django.utils.timezone import now
from celery import shared_task
from .utility import send_email_with_attachments


# Create the looger instance for the celery tasks
logger = logging.getLogger('celery_tasks')


@shared_task
def clean_expired_blacklisted_tokens():
    """
    Deletes expired blacklisted tokens from the database.
    This function queries the BlacklistedToken model for tokens that have expired
    (i.e., their expiration date is less than the current time) and deletes them.
    It logs the number of deleted tokens if successful, or logs an error message
    if an exception occurs during the process.
    Raises:
        Exception: If there is an error during the deletion process.
    """
    
    try:
        expired_tokens = BlacklistedToken.objects.filter(token__expires_at__lt=now())
        count = expired_tokens.count()
        expired_tokens.delete()
        logger.info("Deleted {} expired blacklisted tokens.".format(count))
    except Exception as e:
        logger.error("Failed to delete expired blacklisted tokens: {}".format(e))


@shared_task
def send_email_task(subject, template_name, context, recipient_list, attachments=None):
    """
    Sends an email with the specified subject, template, context, and recipient list, optionally including attachments.
    Args:
        subject (str): The subject of the email.
        template_name (str): The name of the email template to use.
        context (dict): A dictionary of context variables to render the template.
        recipient_list (list): A list of recipient email addresses.
        attachments (list, optional): A list of file attachments to include in the email. Defaults to None.
    Returns:
        NONE.
    """
    
    return send_email_with_attachments(subject, template_name, context, recipient_list, attachments)


@shared_task
def send_otp_email(subject, template_name, context, recipient_list, attachments=None):
    """
    Sends an email with the specified subject, template, context, and recipient list, optionally including attachments.
    Args:
        subject (str): The subject of the email.
        template_name (str): The name of the email template to use.
        context (dict): A dictionary of context variables to render the template.
        recipient_list (list): A list of recipient email addresses.
        attachments (list, optional): A list of file attachments to include in the email. Defaults to None.
    Returns:
        NONE.
    """
    
    return send_email_with_attachments(subject, template_name, context, recipient_list, attachments)
