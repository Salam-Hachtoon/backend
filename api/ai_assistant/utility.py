import logging
from .models import Attachment

# Create a utility logger
logger = logging.getLogger('utility_functions')


def combine_completed_files_content(batch_id):
    """
    Combines the extracted text content of all completed files associated with a given batch ID.

    This function retrieves all attachments linked to the specified batch ID and checks if their
    processing status is marked as "completed". If any file is not completed, an error is logged,
    and a message is returned indicating that not all files have been processed.

    For completed files, the extracted text is concatenated into a single string. If a file has
    an empty extracted text, an error is logged, and the file is skipped.

    Args:
        batch_id (int): The ID of the batch whose attachments are to be processed.

    Returns:
        str: The combined extracted text of all completed files, or a message indicating that
             not all files have been processed.
    """
    for attchemnt in Attachment.objects.filter(batch_id=batch_id):
        if attchemnt.status != "completed":
            logger.error("Not all files have been processed yet.")
            return 'Not all files have been processed yet.'

    combined_text = ""
    for attchemnt in Attachment.objects.filter(batch_id=batch_id):
        if attchemnt.extracted_text == '':
            logger.error("Empty extracted text for file: {}".format(attchemnt.file.name))
            pass
        combined_text += attchemnt.extracted_text + "\n"

    return combined_text
