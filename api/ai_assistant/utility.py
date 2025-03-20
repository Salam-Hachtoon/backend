import logging, requests
from rest_framework.response import Response # type: ignore
from .models import Attachment
from django.conf import settings
from openai import OpenAI


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



def call_deepseek_ai_summary(combined_text):
    """"
    Generates a structured and well-organized summary of the provided text using the DeepSeek AI API.
    The function sends the input text to the DeepSeek AI API with specific summarization guidelines 
    and retrieves a concise summary in a predefined format.
    Args:
        combined_text (str): The input text to be summarized.
    Returns:
        str: The generated summary if successful, or an error message if the operation fails.
    Raises:
        Exception: Logs and handles any exceptions that occur during the API call.
    Example Output Format:
        "The summary of the input text."
    """
    # Crate the payload for the DeepSeek AI API
    Prompt = """
    You are an advanced AI assistant specialized in text summarization. Your task is to generate a structured and well-organized summary of the user-provided text in **JSON format**.  

    ### **Guidelines:**
    1. Begin with a **clear and relevant title** for the summary.  
    2. Follow it with a **short subtitle** that provides additional context.  
    3. Present the summary as a **single, well-structured paragraph** with all key details.  
    4. Ensure clarity, conciseness, and readability while retaining essential information.  
    5. Avoid unnecessary details and redundant words.  

    ### **Expected JSON Output Format:**
    {
    "summary": {
        "content": "<Summary paragraph with key details in a concise manner>"
    }
    }
    """
    try:
        # Initialize the OpenAI client with the DeepSeek API key and base URL
        client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

        # Call the DeepSeek API to generate a summary
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": Prompt},
                {"role": "user", "content": combined_text},
            ],
            stream=False
        )

        # Extract the summary from the response
        summary = response.choices[0].message.content
        return summary

    except Exception as e:
        # Log the error and return a failure message
        logger.error("Failed to generate summary: {}".format(e))
        return "Failed to generate summary"

def call_deepseek_ai_flashcards(summary_content):
    """
    Generates a structured set of flashcards in JSON format by analyzing the provided summary content.
    This function sends a request to the DeepSeek AI API with a prompt to generate flashcards based on the 
    given summary. The flashcards include key terms and their definitions, formatted as a JSON object.
    Args:
        summary_content (str): The summary text to be processed for flashcard generation.
    Returns:
        str: A JSON-formatted string containing the generated flashcards if the API call is successful.
             If the API call fails, returns an error message or a default failure message.
    Raises:
        None: The function handles API errors internally and logs them.
    Example:
        summary = "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods."
        flashcards = call_deepseek_ai_flashcards(summary)
        print(flashcards)
    """

    Prompt = """
    You are an AI assistant skilled in educational content generation. Your task is to analyze the provided summary and generate a structured set of flashcards in JSON format.

    ### **Instructions:**  
    - Extract **key terms** from the summary. These should be important concepts, technical terms, or notable entities.  
    - For each term, provide:  
    - `"term"`: The name of the key concept.  
    - `"definition"`: A concise, clear explanation of the term.  
    - All flashcards must be stored inside a **single key** called `"flashcards"`.  
    - Ensure the output is a **valid JSON object**.

    ### **Text to process:**  
    provided by the user

    ### **Output Format Example:**  
    ```json
    {
    "flashcards": [
        {
        "term": "Photosynthesis",
        "definition": "A process used by plants and other organisms to convert light energy into chemical energy."
        },
        {
        "term": "Chlorophyll",
        "definition": "A green pigment in plants that absorbs light energy for photosynthesis."
        },
        {
        "term": "Carbon Dioxide",
        "definition": "A colorless gas (CO2) absorbed by plants during photosynthesis and released during respiration."
        }
    ]
    }
    """
    payload = {
        "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": Prompt},
                {"role": "user", "content": summary_content}
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
        flash_cards = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No FlashCard generated")
        return flash_cards
    else:
        logger.error("Failed to generate flash cards: {}".format(response.json()))
        return "Failed to generate flash cards"


def call_deepseek_ai_quizes(summary_content, difficulty_level):
    Prompt = """
    You are an AI that generates quizzes based on a given summary. The quiz should be in JSON format with the following structure:

    {
    "quiz": {
        "difficulty": "<easy | medium | hard>",
        "questions": [
        {
            "question_text": "<A well-structured quiz question>",
            "choices": [
            "<Choice 1>",
            "<Choice 2>",
            "<Choice 3>",
            "<Choice 4>"
            ],
            "correct_answer": "<The correct choice from above>"
        }
        ]
    }
    }

    ## Instructions:
    1. Extract key information from the given summary.
    2. Create **3 to 5 multiple-choice questions** based on that information.
    3. Each question should have **4 choices**.
    4. The `"correct_answer"` key should contain the correct choice.
    5. Ensure the difficulty matches the requested level.

    ## Difficulty Level:
    {}

    ## Expected JSON Output:

    """.format(difficulty_level)

    payload = {
        "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": Prompt},
                {"role": "user", "content": summary_content}
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
        flash_cards = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No Quizes generated")
        return flash_cards
    else:
        logger.error("Failed to generate quizes: {}".format(response.json()))
        return "Failed to generate flash quizes"
