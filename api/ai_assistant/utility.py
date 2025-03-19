import logging, requests
from rest_framework.response import Response # type: ignore
from .models import Attachment
from django.conf import settings


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

    return 



def call_deepseek_ai_summary(combined_text):
    """"
    Sends a request to the DeepSeek AI API to generate a structured and concise summary 
    of the provided text based on predefined guidelines.
    Args:
        combined_text (str): The input text to be summarized.
    Returns:
        str: The generated summary if the API call is successful.
        str: An error text with the status code if the API call fails.
    Raises:
        Exception: Logs an error message if the API response status code is not 200.
    Notes:
        - The summary follows a specific format with a title, subtitle, and a single 
          paragraph containing key details.
        - The API key and URL are retrieved from the Django settings.
    """
    # Crate the payload for the DeepSeek AI API
    Prompt = """You are an advanced AI assistant specialized in text summarization. Your task is to generate a structured and well-organized summary of the provided text.  
            ### Guidelines:
            1. Begin with a **clear and relevant title** for the summary.  
            2. Follow it with a **short subtitle** that provides additional context.  
            3. Present the summary as a **single, well-structured paragraph** with all key details.  
            4. Ensure clarity, conciseness, and readability while retaining essential information.  
            5. Avoid unnecessary details and redundant words.  

            ### **Output Format Example:**  
            [Title of the Summary]  
            [Short Subtitle]  
            [Summary paragraph with key details in a concise manner]  
    """
    payload = {
        "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": Prompt},
                {"role": "user", "content": combined_text}
            ],
            "stream": False
    }
    # Send request to DeepSeek API
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(settings.DEEPSEEK_API_KEY)
    }

    response = requests.post(
        settings.DEEPSEEK_API_URL, 
        json=payload,
        headers=headers
    )

    # Handle API response
    if response.status_code == 200:
        summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No summary generated")
        return summary
    else:
        logger.error("Failed to generate summary: {}".format(response.json()))
        return "Failed to generate summary"
