import os, logging
from rest_framework import serializers # type: ignore
from .models import Attachment


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
