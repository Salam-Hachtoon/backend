import logging, requests
from rest_framework.response import Response # type: ignore
from .models import Attachment
from django.conf import settings
import os
import hashlib
import logging
from PyPDF2 import PdfReader
from docx import Document
from pptx import Presentation

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


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


class TextExtractor:
    """
    A utility class for extracting text from files of different formats (PDF, DOCX, and PPTX),
    and generating hash values for provided text.

    make instance from the class and call
    """

    def extract_text(self, file_object):
        """
        Extract text based on the file extension.

        Args:
            file_object (file-like object): The file-like object to extract text from.

        Returns:
            str: The extracted text from the file.

        Raises:
            ValueError: If the file format is unsupported.
        """
        file_name = file_object.name
        ext = os.path.splitext(file_name)[1].lower()
        if ext == ".pdf":
            return self._extract_pdf_text(file_object)
        elif ext == ".docx":
            return self._extract_docx_text(file_object)
        elif ext == ".pptx":
            return self._extract_pptx_text(file_object)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _extract_pdf_text(self, file_object):
        """
        Extract text from a PDF file.

        Args:
            file_object (file-like object): The file-like object representing the PDF file.

        Returns:
            str: The combined text extracted from all pages of the PDF.
        """
        text = []
        pdf = PdfReader(file_object)  # Read the PDF file content
        for page in pdf.pages:
            text.append(page.extract_text())
        return "\n".join(text)

    def _extract_docx_text(self, file_object):
        """
        Extract text from a DOCX file.

        Args:
            file_object (file-like object): The file-like object representing the DOCX file.

        Returns:
            str: The combined text extracted from all paragraphs in the DOCX file.
        """
        text = []
        doc = Document(file_object)  # Open and process the DOCX file
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return "\n".join(text)

    def _extract_pptx_text(self, file_object):
        """
        Extract text from a PPTX file.

        Args:
            file_object (file-like object): The file-like object representing the PPTX file.

        Returns:
            str: The combined text extracted from all slides and text frames in the PPTX file.
        """
        text = []
        prs = Presentation(file_object)
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        text.append(paragraph.text)
        return "\n".join(text)

    def generate_hash(self, text):
        """
        Generate a SHA-256 hash value from the given text.

        Args:
            text (str): The input text to hash.

        Returns:
            str: The hexadecimal representation of the hash value.
        """
        return hashlib.sha256(text.encode()).hexdigest()

    def process_files(self, file_list):
        """
        Process a list of file objects, extract text from each, and return structured output.

        Args:
            file_list (list): A list of file-like objects to process.

        Returns:
            dict: A dictionary containing:
                - data: Concatenated text from all files.
                - hash: SHA-256 hash of the concatenated text.
                - status: Boolean indicating success (True) or failure (False).
                - logerror: String containing error details (null if status is True).
        """
        combined_text = []
        errors = []
        status = True  # Assume success initially
        counter = 0
        for file_object in file_list:
            try:
                extracted_text = self.extract_text(file_object)
                combined_text.append(extracted_text)
                combined_text.append("\n")
                num = "FILE#{}\n".format(counter)
                line = "_________________________________________________________________________________________________\n"
                counter+=1
                combined_text.append(line + num)
            except Exception as e:
                # Log the error and add it to the errors list
                error_message = f"Error processing file {file_object.name}: {str(e)}"
                errors.append(error_message)
                status = False  # Set status to False if any error occurs

        # Combine all extracted text
        final_text = "\n".join(combined_text) if combined_text else None

        # Generate hash of the combined text
        text_hash = self.generate_hash(final_text) if final_text else None

        # Prepare the output
        output = {
            "data": final_text,
            "hash": text_hash,
            "status": status,
            "logerror": "\n".join(errors) if not status else None,
        }

        return output