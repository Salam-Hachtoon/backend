import os, logging
from rest_framework import serializers # type: ignore
from .models import Attachment, Summary, FlashCard, Question, Quiz, Choice


# Create the looger instance for the attachment model
logger = logging.getLogger('attachment_serializer')


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Attachment model.
    This serializer is used to convert Attachment model instances into JSON format
    and vice versa. It includes the following fields:
    - `id`: The unique identifier of the attachment.
    - `file`: The file associated with the attachment.
    - `extracted_text`: The text extracted from the file (read-only).
    - `status`: The processing status of the attachment (read-only).
    - `uploaded_at`: The timestamp when the attachment was uploaded (read-only).
    Read-only fields:
    - `extracted_text`
    - `status`
    - `uploaded_at`
    """

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'extracted_text', 'status', 'uploaded_at', 'batch_id']
        read_only_fields = ['extracted_text', 'status', 'uploaded_at', 'batch_id']

class MultiFileUploadSerializer(serializers.Serializer):
    """
    Serializer for handling multiple file uploads.
    Attributes:
        files (ListField): A list of files to be uploaded. Each file is validated
            using the `FileField` serializer. The list cannot be empty and is
            write-only.
    Methods:
        validate_files(files):
            Validates each file in the uploaded list. Ensures that the file
            extensions are among the allowed types ('pdf', 'doc', 'docx', 'txt')
            and that the file size does not exceed 10MB. Raises a
            `serializers.ValidationError` if any file fails validation.
    """

    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        write_only=True
    )

    def validate_files(self, files):
        """
        Validate each file in the list of uploaded files.
        """
        allowed_file_extensions = ['pdf', 'doc', 'docx', 'txt']
        allowed_file_size = 10 * 1024 * 1024  # 10MB

        for file in files:
            file_extension = os.path.splitext(file.name)[1][1:].lower()
            if file_extension not in allowed_file_extensions:
                logger.error(f"Unsupported file extension: {file.name}. Allowed: pdf, doc, docx, txt.")
                raise serializers.ValidationError(
                    "Unsupported file extension for file {}. Allowed: pdf, doc, docx, txt.".format(file.name)
                )

            if file.size > allowed_file_size:
                logger.error("The file {} is too large. Max size: 10MB.".format(file.name))
                raise serializers.ValidationError(
                    "The file {} is too large. Max size: 10MB.".format(file.name)
                )
        return files


class SummarySerializer(serializers.ModelSerializer):
    """
    Serializer for the Summary model.
    This serializer is used to convert Summary model instances into JSON format
    and validate incoming data for creating or updating Summary objects.
    Fields:
    - id (read-only): The unique identifier of the summary.
    - user (read-only): The user associated with the summary.
    - attachment: The file or document attached to the summary.
    - content: The textual content of the summary.
    - created_at (read-only): The timestamp when the summary was created.
    Read-only fields:
    - id
    - user
    - created_at
    """

    class Meta:
        model = Summary
        fields = ['id', 'user', 'attachment', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class FlashCardSerializer(serializers.ModelSerializer):
    """
    Serializer for the FlashCard model.
    This serializer is used to convert FlashCard model instances into JSON format
    and validate data for creating or updating FlashCard instances.
    Attributes:
        Meta (class): Contains metadata for the serializer.
            - models: Specifies the FlashCard model to be serialized.
            - fields: Lists the fields to be included in the serialized output.
            - read_only_fields: Specifies fields that are read-only and cannot be modified.
    """

    class Meta:
        models = FlashCard
        fields = ['id', 'summary', 'term', 'definition', 'created_at']
        read_only_fields = ['id', 'summary', 'created_at']


class ChoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Choice model.
    This serializer is used to convert Choice model instances into JSON format
    and validate incoming data for creating or updating Choice instances.
    Fields:
    - id: The unique identifier for the choice.
    - choice_text: The text of the choice.
    - is_correct: A boolean indicating whether the choice is correct.
    """

    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Question model.
    This serializer is used to convert Question model instances into JSON format
    and vice versa. It includes the following fields:
    - `id`: The unique identifier for the question.
    - `question_text`: The text of the question.
    - `correct_answer`: The correct answer to the question.
    - `choices`: A nested serializer for the related Choice objects, which are
        read-only and allow multiple choices to be represented.
    Attributes:
            choices (ChoiceSerializer): A nested serializer for the related choices.
    """

    choices = ChoiceSerializer(many=True, read_only=True)  # Nested serializer for choices

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'correct_answer', 'choices']


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for the Quiz model.
    This serializer is used to convert Quiz model instances into JSON format and vice versa.
    It includes a nested serializer for the related questions.
    Attributes:
        questions (QuestionSerializer): A nested serializer for the related questions, 
            set to read-only and allows multiple questions.
    Meta:
        model (Quiz): The model that this serializer is based on.
        fields (list): Specifies the fields to include in the serialized output. 
            Includes 'id', 'user', 'summary', 'difficulty', 'created_at', and 'questions'.
        read_only_fields (list): Specifies the fields that are read-only. 
            Includes 'id', 'user', 'created_at', and 'questions'.
    """

    questions = QuestionSerializer(many=True, read_only=True)  # Nested serializer for questions

    class Meta:
        model = Quiz
        fields = ['id', 'user', 'summary', 'difficulty', 'created_at', 'questions']
        read_only_fields = ['id', 'user', 'created_at', 'questions']