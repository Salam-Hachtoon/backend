import logging
from celery import shared_task
from .models import Attachment
from .utility import extract_pdf_text, extract_docx_text, extract_pptx_text

# Get an instance of a logger
logger = logging.getLogger('attachment_process_file')

@shared_task
def extract_pdf_task(attachment_id):
    """
    Extracts text from a PDF file associated with an attachment and updates the attachment's status.
    This function retrieves an attachment by its ID, extracts text from the associated PDF file,
    and updates the attachment's `extracted_text` and `status` fields. If an error occurs during
    the process, the attachment's status is updated to "failed", and the error is logged.
    Args:
        attachment_id (int): The ID of the attachment to process.
    Raises:
        Exception: If an error occurs during text extraction or database operations.
    Side Effects:
        - Updates the `extracted_text` and `status` fields of the `Attachment` object in the database.
        - Logs an error message if the operation fails.
    """

    try:
        attachment = Attachment.objects.get(id=attachment_id)
        extracted_text = extract_pdf_text(attachment.file.path)
        attachment.extracted_text = extracted_text
        attachment.status = "completed"
        attachment.save()
    except Exception as e:
        attachment = Attachment.objects.get(id=attachment_id)
        attachment.status = "failed"
        attachment.save()
        logger.error("Failed to extract text from PDF for attachment {}: {}".format(attachment_id=attachment_id, e=e))

@shared_task
def extract_docx_task(attachment_id):
    """
    Extracts text from a DOCX file associated with the given attachment ID and updates the attachment's status.
    This function retrieves an attachment object by its ID, extracts text from the associated DOCX file,
    and updates the attachment's `extracted_text` and `status` fields. If an error occurs during the process,
    the attachment's status is updated to "failed", and the error is logged.
    Args:
        attachment_id (int): The ID of the attachment to process.
    Raises:
        Exception: If an error occurs during text extraction or database operations.
    Side Effects:
        - Updates the `extracted_text` and `status` fields of the `Attachment` object in the database.
        - Logs errors if the text extraction process fails.
    """

    try:
        attachment = Attachment.objects.get(id=attachment_id)
        extracted_text = extract_docx_text(attachment.file.path)
        attachment.extracted_text = extracted_text
        attachment.status = "completed"
        attachment.save()
    except Exception as e:
        attachment = Attachment.objects.get(id=attachment_id)
        attachment.status = "failed"
        attachment.save()
        logger.error("Failed to extract text from DOCX for attachment {}: {}".format(attachment_id=attachment_id, e=e))


@shared_task
def extract_txt_task(attachment_id):
    """ Celery task to extract text from a TXT file and update the corresponding 
    Attachment object with the extracted text and status.

    Args:
        attachment_id (int): The ID of the Attachment object to process.

    Raises:
        Exception: If an error occurs during text extraction or file handling.

    Behavior:
        - Retrieves the Attachment object using the provided ID.
        - Reads the content of the TXT file associated with the Attachment.
        - Updates the Attachment object with the extracted text and sets its 
          status to "completed" upon success.
        - If an error occurs, sets the Attachment status to "failed" and logs 
          the error.
    """

    try:
        attachment = Attachment.objects.get(id=attachment_id)
        with open(attachment.file.path, 'r') as file:
            extracted_text = file.read()
        attachment.extracted_text = extracted_text
        attachment.status = "completed"
        attachment.save()
    except Exception as e:
        attachment = Attachment.objects.get(id=attachment_id)
        attachment.status = "failed"
        attachment.save()
        logger.error("Failed to extract text from TXT for attachment {}: {}".format(attachment_id=attachment_id, e=e))

@shared_task
def extract_pptx_task(attachment_id):
    """
    Extracts text from a PPTX file associated with the given attachment ID and updates the attachment's status.
    This function retrieves an attachment object by its ID, extracts text from the associated PPTX file,
    and updates the attachment's `extracted_text` and `status` fields. If an error occurs during the process,
    the attachment's status is updated to "failed", and the error is logged.
    Args:
        attachment_id (int): The ID of the attachment to process.
    Raises:
        Exception: If an error occurs during text extraction or database operations.
    Side Effects:
        - Updates the `extracted_text` and `status` fields of the `Attachment` object in the database.
        - Logs an error message if the operation fails.
    """

    try:
        attachment = Attachment.objects.get(id=attachment_id)
        extracted_text = extract_pptx_text(attachment.file.path)
        attachment.extracted_text = extracted_text
        attachment.status = "completed"
        attachment.save()
    except Exception as e:
        attachment = Attachment.objects.get(id=attachment_id)
        attachment.status = "failed"
        attachment.save()
        logger.error("Failed to extract text from PPTX for attachment {}: {}".format(attachment_id=attachment_id, e=e))
