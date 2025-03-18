import logging
from rest_framework.decorators import api_view, permission_classes  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.permissions import AllowAny  # type: ignore
from rest_framework import status  # type: ignore
from .serializers import UserSerializer
from .Google_OAuth_API import exchange_code_for_token, exchange_token_for_user_info
from .models import User
from .utility import generate_jwt_tokens, 



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


logger = logging.getLogger(__name__)

@api_view(["GET"])
@permission_classes([AllowAny])
def google_auth_callback(request):
    """
    Handle the Google OAuth callback.
    
    Steps:
    1. Retrieve the authorization code from the request.
    2. Exchange the code for tokens (access token, ID token).
    3. Use the access token to get the user's information.
    4. Create or update the user in the database.
    5. Return a success response with serialized user data .
    """
    # Retrieve the authorization code from query parameters
    code = request.GET.get("code")
    if not code:
        logger.error("No authorization code provided in the request.")
        return Response(
            {"error": "No authorization code provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Exchange the authorization code for tokens
    tokens = exchange_code_for_token(code)
    if tokens is None:
        logger.error("Failed to exchange code for tokens.")
        return Response(
            {"error": "Failed to get tokens from Google"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Extract the access token from the response
    access_token = tokens.get("access_token")
    if not access_token:
        logger.error("No access token found in token response.")
        return Response(
            {"error": "No access token provided by Google"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Exchange the access token for user info
    user_info = exchange_token_for_user_info(access_token)
    if user_info is None:
        logger.error("Failed to exchange token for user info.")
        return Response(
            {"error": "Failed to get user info from Google"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Retrieve user information from the user_info dictionary
    email = user_info.get("email")
    first_name = user_info.get("first_name")
    last_name = user_info.get("last_name")
    profile_picture = user_info.get("profile_picture")
    
    if not email:
        logger.error("No email found in Google user info.")
        return Response(
            {"error": "Email not found in Google user info"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create or update the user in your database
    user, created = User.objects.get_or_create(email=email, defaults={
        "first_name": first_name,
        "last_name": last_name,
        "profile_picture": profile_picture,
    })
    
    # # Optionally, update the user if information has changed
    # if not created:
    #     updated = False
    #     if user.first_name != first_name:
    #         user.first_name = first_name
    #         updated = True
    #     if user.last_name != last_name:
    #         user.last_name = last_name
    #         updated = True
    #     if user.profile_picture != profile_picture:
    #         user.profile_picture = profile_picture
    #         updated = True
    #     if updated:
    #         user.save()
    
    # Serialize the user data
    serializer = UserSerializer(user)
    
    return Response({
        "message": "Authentication successful",
        "user": serializer.data,
    }, status=status.HTTP_200_OK)
