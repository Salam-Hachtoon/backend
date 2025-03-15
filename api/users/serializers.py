import os, logging
from rest_framework import serializers
from .models import User


# Create the looger instance for the celery tasks
logger = logging.getLogger('user_serializer')


class UserSerializer(serializers.ModelSerializer):
    """
    UserSerializer is a Django REST framework serializer for the User model.
    Attributes:
        password (serializers.CharField): A write-only field for the user's password with a minimum length of 6 characters.
    Meta:
        model (User): The model that is being serialized.
        fields (list): A list of fields to be included in the serialized output.
    Methods:
        validate_profile_picture(image):
            Validates the profile picture to ensure it has an allowed file extension (jpg, jpeg, png) and does not exceed the maximum size of 5MB.
            Args:
                image (File): The profile picture file to be validated.
            Returns:
                File: The validated profile picture file.
            Raises:
                serializers.ValidationError: If the file extension is not allowed or the file size exceeds the limit.
        create(validated_data):
            Creates a new user with the validated data.
            Args:
                validated_data (dict): The validated data for creating a new user.
            Returns:
                User: The newly created user instance.
    """

    # Set the password field as write-only to prevent it from being serialized
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'profile_picture',
            'password',
        ]

    def validate_profile_picture(self, image):
        allowed_image_extensions = ['jpg', 'jpeg', 'png']
        allowed_image_size = 5 * 1024 * 1024  # 5MB

        image_extension = os.path.splitext(image.name)[1][1:].lower()
        if image_extension not in allowed_image_extensions:
            logger.error('Unsupported file extension. Allowed: jpg, jpeg, png.')
            raise serializers.ValidationError(
                'Unsupported file extension. Allowed: jpg, jpeg, png.'
            )

        if image.size > allowed_image_size:
            logger.error('The image is too large. Max size: 5MB.')
            raise serializers.ValidationError(
                'The image is too large. Max size: 5MB.'
            )
        return image

    def create(self, validated_data):
        # Create a new user with the validated data
        return User.objects.create_user(**validated_data)
