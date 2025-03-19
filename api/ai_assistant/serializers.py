import os, logging
from rest_framework import serializers # type: ignore
from .models import attachment


# Create the looger instance for the attachment model
logger = logging.getLogger('attachment_serializer')


class attachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for handling file attachments.
    This serializer validates and processes file attachments uploaded by users. 
    It ensures that the file meets specific requirements, such as allowed file 
    extensions and maximum file size.
    Attributes:
        Meta:
            model (Model): The model associated with this serializer (attachment).
            fields (list): The fields to include in the serialized output ('user', 'file').
            extra_kwargs (dict): Additional keyword arguments for field validation.
    Methods:
        validate_file(file):
            Validates the uploaded file to ensure it has an allowed extension and 
            does not exceed the maximum file size.
            Args:
                file (File): The uploaded file to validate.
            Returns:
                File: The validated file.
            Raises:
                serializers.ValidationError: If the file has an unsupported extension 
                or exceeds the maximum allowed size.
    """

    class Meta:
        model = attachment
        fields = [
            'user',
            'file'
        ]
        extra_kwargs = {
            'user': {'required': True},
            'file': {'required': True}
        }

    def validate_file(self, file):
        allowed_file_extensions = ['pdf', 'doc', 'docx', 'txt']
        allowed_file_size = 10 * 1024 * 1024  # 10MB

        file_extension = os.path.splitext(file.name)[1][1:].lower()
        if file_extension not in allowed_file_extensions:
            logger.error('Unsupported file extension. Allowed: pdf, doc, docx, txt.')
            raise serializers.ValidationError(
                'Unsupported file extension. Allowed: pdf, doc, docx, txt.'
            )

        if file.size > allowed_file_size:
            logger.error('The file is too large. Max size: 10MB.')
            raise serializers.ValidationError(
                'The file is too large. Max size: 10MB.'
            )
        return file
