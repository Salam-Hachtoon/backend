import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Attachment
from .celery_tasks import extract_pdf_task, extract_docx_task, extract_txt_task, extract_pptx_task
from .utility import check_file_type


logger = logging.getLogger('attachment_process_file')


@receiver(post_save, sender=Attachment)
def process_attachment(sender, instance, created, **kwargs):
    """"
    Signal handler to process an attachment after it is saved.

    This function is triggered when an attachment instance is saved. If the instance
    is newly created, it updates the attachment's status to "processing" and determines
    the file type of the attachment. Based on the file type, it dispatches the appropriate
    Celery task to process the file. If the file type is unsupported or an error occurs
    during processing, the attachment's status is updated to "failed" and an error is logged.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Model instance): The instance of the model that was saved.
        created (bool): A boolean indicating whether the instance was created.
        **kwargs: Additional keyword arguments.

    Raises:
        Exception: Logs any exceptions that occur during processing and updates the
                   attachment's status to "failed".
    Signal to process an attachment after it is saved.
    """
    if created:  # Only process newly created attachments
        try:
            # Update the attachment status to "processing"
            instance.status = "processing"
            instance.save()

            # Check the file type
            file_type = check_file_type(instance.file.name)

            # Call the appropriate Celery task based on the file type
            if file_type == 'pdf':
                extract_pdf_task.delay(instance.id)
            elif file_type == 'docx':
                extract_docx_task.delay(instance.id)
            elif file_type == 'pptx':
                extract_pptx_task.delay(instance.id)
            else:
                # Unsupported file type
                instance.status = "failed"
                instance.save()
                logger.error("Unsupported file type for attachment: {}".format(instance.file.name))

        except Exception as e:
            # Log any errors
            instance.status = "failed"
            instance.save()
            logger.error("Failed to process attachment: {}".format(e))
