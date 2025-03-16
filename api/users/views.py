import logging
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import AllowAny # type: ignore
from rest_framework import status # type: ignore
from .serializers import UserSerializer
from .models import User

# Create the looger instance for the celery tasks
loger = logging.getLogger('requests')


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    Handle user signup request.
    This view function handles the user signup process. It checks if a user with the provided email
    already exists. If the user exists, it returns a 400 Bad Request response with an appropriate
    error message. If the user does not exist, it validates the provided data using the UserSerializer.
    If the data is valid, it saves the new user and returns a 201 Created response with a success message
    and the user data. If the data is not valid, it returns a 400 Bad Request response with the validation
    errors.
    Args:
        request (HttpRequest): The HTTP request object containing the user data.
    Returns:
        Response: A DRF Response object with the appropriate status and message.
    """
    
    serializer = UserSerializer(data=request.data)
    if User.objects.filter(email=request.data['email']).exists():
        # Log the error message
        loger.error('User already exists.')
        return Response(
            {
                'message': 'User already exists.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'message': 'User created successfully.',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    else:
        # Log the error message
        loger.error('User creation failed: {}.'.format(serializer.errors))
        return Response(
            {
                'message': 'User creation failed.',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
