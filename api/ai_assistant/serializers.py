import os, logging
from rest_framework import serializers # type: ignore
from .models import attachment


# Create the looger instance for the attachment model
logger = logging.getLogger('attachment_serializer')


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