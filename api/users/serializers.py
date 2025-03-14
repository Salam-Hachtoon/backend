import os
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    UserSerializer is a ModelSerializer for the User model.
    Fields:
        - email: The email address of the user.
        - first_name: The first name of the user.
        - last_name: The last name of the user.
        - profile_picture: The profile picture of the user.
        - password: The password of the user (write-only, minimum length of 6 characters).
    Methods:
        - create(validated_data): Creates a new user with the validated data.
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
        ]

    def create(self, validated_data):
        # Create a new user with the validated data
        return User.objects.create_user(**validated_data)
