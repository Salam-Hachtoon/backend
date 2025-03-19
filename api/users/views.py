import logging
from rest_framework.decorators import api_view, permission_classes  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
from rest_framework import status  # type: ignore
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from .Google_OAuth_API import exchange_code_for_token, exchange_token_for_user_info
from .models import User
from .utility import generate_jwt_tokens
from django.http import JsonResponse


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


@api_view(['POST'])
@permission_classes([AllowAny])
def signin(request):
    """
    Handle user sign-in.
    This view function handles the sign-in process for users. It expects an HTTP request
    containing 'email' and 'password' in the request data. If the credentials are valid,
    it authenticates the user and generates JWT tokens for the authenticated user.
    Args:
        request (HttpRequest): The HTTP request object containing user credentials.
    Returns:
        Response: A DRF Response object containing a success message and JWT tokens if
                  authentication is successful, or an error message if authentication fails.
    Raises:
        KeyError: If 'email' or 'password' is not provided in the request data.
    """

    try:
        email = request.data['email']
        password = request.data['password']
    except KeyError:
        loger.error('Email and password are required.')
        return Response(
            {
                'message': 'Email and password are required.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Authenticate the user
    user = authenticate(request, email=email, password=password)
    # If the user is not authenticated, return an error response
    if not user:
        loger.error('Invalid credentials.')
        return Response(
            {
                'message': 'Invalid credentials.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Generate JWT tokens for the authenticated user
    access_token, refresh_token = generate_jwt_tokens(user)
    return Response(
        {
            'message': 'Login successful.',
            'access_token': access_token,
            'refresh_token': refresh_token
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signout(request):
    """
    Handles the signout process by blacklisting the provided refresh token.
    Args:
        request (Request): The HTTP request object containing the refresh token.
    Returns:
        Response: A response object indicating the result of the signout process.
            - If the refresh token is not provided, returns a 400 BAD REQUEST response with an error message.
            - If the refresh token is successfully blacklisted, returns a 200 OK response with a success message.
            - If an error occurs during the process, returns a 400 BAD REQUEST response with an error message.
    """

    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        loger.error('Refresh token is required.')
        return Response(
            {
                'message': 'Refresh token is required.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create a token object from the refresh token and blacklist it
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {
                'message': 'Logout successful.'
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        # Catch any exceptions and log the error message
        loger.error('Error logging out: {}'.format(str(e)))
        return Response(
            {
                'message': 'Error logging out.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


def google_oauth_callback(request):
    """
    Handles the OAuth2 callback from Google.
    """
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Authorization code not provided"}, status=400)

    # Step 1: Exchange code for access token
    token_response = exchange_code_for_token(code)
    if not token_response:
        return JsonResponse({"error": "Failed to obtain access token"}, status=400)

    access_token = token_response.get("access_token")

    # Step 2: Get user info
    user_info = exchange_token_for_user_info(access_token)
    if not user_info:
        return JsonResponse({"error": "Failed to obtain user info"}, status=400)

    email = user_info.get("email")
    first_name = user_info.get("given_name")
    last_name = user_info.get("family_name")
    profile_picture = user_info.get("picture")

    # Step 3: Create or update the user
    user, created = User.objects.get_or_create(email=email, defaults={
        "first_name": first_name,
        "last_name": last_name,
        "profile_picture": profile_picture
    })

    # Step 4: Generate JWT Token

    # If the user is not authenticated, return an error response
    if not user:
        loger.error('Invalid credentials.')
        return Response(
            {
                'message': 'Invalid authentication .'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Generate JWT tokens for the authenticated user
    access_token, refresh_token = generate_jwt_tokens(user)
    return Response(
        {
            'message': 'Login successful.',
            'access_token': access_token,
            'refresh_token': refresh_token
        },
        status=status.HTTP_200_OK
    )
