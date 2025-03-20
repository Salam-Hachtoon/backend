import logging, time
from rest_framework import status # type: ignore
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from .serializers import MultiFileUploadSerializer, AttachmentSerializer, SummarySerializer, FlashCardSerializer, QuizSerializer
from .models import Attachment, Summary, FlashCard, Quiz
from .utility import combine_completed_files_content, call_deepseek_ai_summary, call_deepseek_ai_flashcards, call_deepseek_ai_quizes

#  Create the looger instance for the requests module
loger = logging.getLogger('requests')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_attachments(request):
    """
    Handles the upload of multiple file attachments.
    This view allows authenticated users to upload up to three files at a time.
    It validates the uploaded files using a serializer, creates attachment
    instances for each file, and associates them with the authenticated user.
    Args:
        request (HttpRequest): The HTTP request object containing the uploaded
        files and user information.
    Returns:
        Response: A DRF Response object containing a success message and the
        serialized data of the uploaded attachments if the operation is
        successful. If the file limit is exceeded or the data is invalid, it
        returns an error message with a 400 status code.
    Raises:
        None
    Notes:
        - The maximum number of files allowed per request is 3.
        - Each file is associated with the authenticated user and given a
          default status of 'pending'.
    """

    files = request.FILES.getlist("files")

    if len(files) > 3:
        return Response(
            {
                "message": "Maximum file limit exceeded. Only 3 files are allowed."
            }
            , status=status.HTTP_400_BAD_REQUEST
        )

    serializer = MultiFileUploadSerializer(data=request.data)
    if not serializer.is_valid():
        loger.error("Invalid file upload data.")
        return Response(
            {
                'message': 'Invalid file upload data.',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    files = serializer.validated_data['files']  # Get the list of validated files from the serializer
    user = request.user  # Get the authenticated user
    attachments = []
    batch_id = str(int(time.time()))  # Create a unique batch ID (current UNIX timestamp)

    for file in files: # Iterate over the list of files
        # Create an attachment instance for each file
        attachment_instance = Attachment.objects.create(
            user=user,  # Associate the attachment with the authenticated user
            file=file,
            status='pending',  # Default status
            batch_id=batch_id  # Assign the batch ID to the attachment
        )
        attachments.append(attachment_instance)

    # Serialize the list of attachment instances
    response_serializer = AttachmentSerializer(attachments, many=True)
    return Response(
        {
            'message': 'Files uploaded successfully.',
            'data': response_serializer.data
        },
        status=status.HTTP_201_CREATED
    )



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_summary(request):
    """
    Handles the generation of a summary for a batch of files.
    This view function processes a batch of files identified by a batch ID, 
    combines their content, and generates a summary using an external AI service. 
    The generated summary is saved to the database and returned in the response.
    Args:
        request (HttpRequest): The HTTP request object containing user information 
                               and batch ID in the request data.
    Returns:
        Response: A Django REST framework Response object with the following:
            - HTTP 201 Created: If the summary is successfully generated and saved.
            - HTTP 400 Bad Request: If the batch ID is not provided or not all files 
              in the batch have been processed.
            - HTTP 404 Not Found: If no files are found for the given batch ID.
            - HTTP 500 Internal Server Error: If the summary generation fails.
    Raises:
        KeyError: If the batch ID is not provided in the request data.
    Workflow:
        1. Retrieve the authenticated user from the request.
        2. Extract the batch ID from the request data.
        3. Query the database for attachments associated with the batch ID.
        4. Combine the content of all completed files in the batch.
        5. Call an external AI service to generate a summary from the combined content.
        6. Save the generated summary to the database.
        7. Serialize and return the summary in the response.
    """

    user = request.user  # Get the authenticated user
    try:
        batch_id = request.data.get('batch_id')
    except KeyError:
        loger.error("Batch ID not provided.")
        return Response(
            {
                "message": "Batch ID not provided."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Query all attachments with the given batch_id
    attachments = Attachment.objects.filter(batch_id=batch_id)

    if not attachments.exists():
        loger.error("No files found for batch ID: {}".format(batch_id=batch_id))
        return Response(
            {
                "message": "No files found for batch ID: {}".format(batch_id)
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Combine the extracted text content of all completed files
    combined_text = combine_completed_files_content(batch_id)
    if combined_text == 'Not all files have been processed yet.':
        return Response(
            {
                "message": "Not all files have been processed yet."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    deepseek_response = call_deepseek_ai_summary(combined_text)
    if deepseek_response == "Failed to generate summary":
        return Response(
            {
                "message": "Failed to generate summary."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    # Creates the new summary
    new_summary = Summary.objects.create(
        user=user,
        content=deepseek_response
    )
    new_summary.save()

    # Serialize the created summary
    serializer = SummarySerializer(new_summary)
    return Response(
        {
            "message": "Summary created successfully.",
            "data": serializer.data
        },
        status=status.HTTP_201_CREATED
    )



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_flash_cards(request):
    """
    Generate and save flashcards for a given summary.
    This view retrieves a summary by its ID, generates flashcards using an AI service,
    and saves the flashcards to the database. The flashcards are then serialized and
    returned in the response.
    Args:
        request (HttpRequest): The HTTP request object containing user authentication
            and the summary ID in the request data.
    Returns:
        Response: A DRF Response object containing:
            - HTTP 201: If flashcards are successfully generated and saved.
            - HTTP 400: If the summary ID is not provided in the request data.
            - HTTP 404: If the summary with the given ID does not exist for the user.
            - HTTP 500: If the AI service fails to generate flashcards.
    Raises:
        KeyError: If the 'id' key is missing in the request data.
    Notes:
        - The function uses the `call_deepseek_ai_flashcards` function to generate
          flashcards from the summary content.
        - Flashcards are created and saved in the `FlashCard` model.
        - The response includes serialized flashcard data using `FlashCardSerializer`.
    """

    user = request.user  # Get the authenticated user
    try:
        id = request.data.get('id')
    except KeyError:
        loger.error("Summary ID not provided.")
        return Response(
            {
                "message": "Summary ID not provided."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        # Query all Summary with the given id
        summary = Summary.objects.get(
            id=id,
            user=user
        )
    except Summary.DoesNotExist:
        loger.error("Summary with ID {} not found.".format(id))
        return Response(
            {
                "message": "Summary with ID {} not found.".format(id)
            },
            status=status.HTTP_404_NOT_FOUND
        )

    deepseek_response = call_deepseek_ai_flashcards(summary.content)
    if deepseek_response == "Failed to generate flash cards":
        return Response(
            {
                "message": "Failed to generate  flash cards."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Create flashcards from the DeepSeek response
    flashcards_data = deepseek_response.get("flashcards", [])
    created_flashcards = []
    for flashcard in flashcards_data:
        term = flashcard.get("term")
        definition = flashcard.get("definition")

        if term and definition:
            # Create and save the flashcard
            flashcard_instance = FlashCard.objects.create(
                summary=summary,
                term=term,
                definition=definition
            )
            created_flashcards.append(flashcard_instance)

    # Serialize the created flashcards
    serializer = FlashCardSerializer(created_flashcards, many=True)
    return Response(
        {
            "message": "Flashcards generated and saved successfully.",
            "data": serializer.data
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_quiz(request):
    user = request.user  # Get the authenticated user
    try:
        summary_id = request.data.get('id')
        difficulty_level = request.data.get('difficulty')
    except KeyError:
        loger.error("Eather summary id or difficulty level not provided.")
        return Response(
            {
                "message": "Eather summary id or difficulty level not provided."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Query all Summary with the given id
        summary = Summary.objects.get(
            id=summary_id,
            user=user
        )
    except Summary.DoesNotExist:
        loger.error("Summary with ID {} not found.".format(id))
        return Response(
            {
                "message": "Summary with ID {} not found.".format(id)
            },
            status=status.HTTP_404_NOT_FOUND
        )
    deepseek_response = call_deepseek_ai_quizes(summary.content, difficulty_level)
    if deepseek_response == "Failed to generate quiz":
        return Response(
            {
                "message": "Failed to generate quiz."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Extract quiz data from the DeepSeek response
    quiz_data = deepseek_response.get("quiz", {})
    difficulty = quiz_data.get("difficulty")
    questions_data = quiz_data.get("questions", [])

    # Create the Quiz object
    quiz = Quiz.objects.create(
        summary=summary,
        difficulty=difficulty,
        user=user
    )

    # Create questions and choices
    created_questions = []
    for question_data in questions_data:
        question_text = question_data.get("question_text")
        choices = question_data.get("choices", [])
        correct_answer = question_data.get("correct_answer")

        # Create the Question object
        question = quiz.questions.create(
            question_text=question_text,
            correct_answer=correct_answer
        )
        created_questions.append(question)

        # Create the Choice objects
        for choice_text in choices:
            question.choices.create(
                choice_text=choice_text,
                is_correct=(choice_text == correct_answer)
            )

    # Serialize the created quiz and its questions
    serializer = QuizSerializer(quiz)
    return Response(
        {
            "message": "Quiz generated and saved successfully.",
            "data": serializer.data
        },
        status=status.HTTP_201_CREATED
    )
