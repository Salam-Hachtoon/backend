import os, logging
from rest_framework import serializers # type: ignore
from .models import User


# Create the looger instance for the celery tasks
logger = logging.getLogger('user_serializer')


class UserSerializer(serializers.ModelSerializer):
    """
    UserSerializer is a Django REST Framework serializer for the User model.
    Fields:
        email (str): The email address of the user. Required.
        first_name (str): The first name of the user. Required.
        last_name (str): The last name of the user. Required.
        profile_picture (ImageField): The profile picture of the user. Optional.
        password (str): The password of the user. Required. Write-only. Minimum length of 6 characters.
        gender (str): The gender of the user. Required.
    Methods:
        validate_profile_picture(image):
            Validates the profile picture to ensure it has an allowed file extension (jpg, jpeg, png)
            and does not exceed the maximum size of 5MB.
            Args:
                image (ImageField): The profile picture to validate.
            Returns:
                ImageField: The validated profile picture.
            Raises:
                serializers.ValidationError: If the file extension is not allowed or the image size exceeds 5MB.
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
            'gender'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
            'gender': {'required': False}
        }

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


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    This serializer handles the following fields:
    - email: The user's email address.
    - first_name: The user's first name.
    - last_name: The user's last name.
    - profile_picture: The user's profile picture. The image must be in jpg, jpeg, or png format and must not exceed 5MB in size.
    - password: The user's password. This field is write-only and must be at least 6 characters long.
    - gender: The user's gender.
    Methods:
    - validate_profile_picture(image): Validates the profile picture to ensure it has a supported file extension and does not exceed the maximum allowed size.
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
            'gender'
        ]

    def  validate_profile_picture(self, image):
            allowed_image_extensions = ['jpg', 'jpeg', 'png']
            allowed_image_size = 5 * 1024 * 1024 # 5MB

            image_extension = os.path.splitext(image.name)[1][1:].lower()
            if image_extension not in allowed_image_extensions:
                raise serializers.ValidationError(
                    'Unsupported file extension. Supported extensions are jpg, jpeg, and png.'
                )

            if image.size > allowed_image_size:
                raise serializers.ValidationError(
                    'The image size is too large. The maximum image size is 5MB.'
                )
            return image
