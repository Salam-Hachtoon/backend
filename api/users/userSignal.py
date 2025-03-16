from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from .celery_tasks import send_email_task


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Sends a welcome email to a new user upon creation.
    This function is intended to be used as a Django signal handler for the
    post_save signal of the User model. When a new user instance is created,
    it sends a welcome email to the user's email address.
    Args:
        sender (Model): The model class that sent the signal.
        instance (User): The actual instance being saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments.
    Returns:
        None
    """

    # Only if a new user instance is created
    if created:
        subject = 'Welcome to IASQ AI! 🚀 Your AI Journey Starts Now'
        # The template_name should be the same name as the email html version and plane text version
        template_name = 'welcome'
        # Data to be passed to the email template from the user instance
        context = {
            'first_name': instance.first_name,
        }
        # Recipient list should be a list of email addresses
        recipient_list = [instance.email]
        attachments = None
        # Call Celery task asynchronously
        send_email_task.delay(subject, template_name, context, recipient_list, attachments)
    else:
        print('No email sent')
