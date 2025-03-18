import logging
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from rest_framework import status # type: ignore
from django.contrib.auth import authenticate
from .serializers import UserSerializer, UserUpdateSerializer
from .models import User
from .utility import generate_jwt_tokens
from .celery_tasks import send_otp_email

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
    containing 'email' and 'password' in the request data. The function performs the following steps:
    1. Extracts 'email' and 'password' from the request data.
    2. Authenticates the user using the provided credentials.
    3. If authentication fails, returns a 400 Bad Request response with an error message.
    4. If authentication succeeds, generates JWT tokens (access and refresh tokens).
    5. Returns a 200 OK response with the access token and sets the refresh token as an HTTP-only cookie.
    Args:
        request (HttpRequest): The HTTP request object containing user credentials.
    Returns:
        Response: An HTTP response with a status code and a message.
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
        response = Response(
            {
                'message': 'Invalid credentials.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        return response

    # Generate JWT tokens for the authenticated user
    access_token, refresh_token = generate_jwt_tokens(user)
    response = Response(
        {
            'message': 'Login successful.',
            'access_token': access_token,
            # 'refresh_token': refresh_token
        },
        status=status.HTTP_200_OK
    )

    # Set refresh token as an HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=str(refresh_token),
        httponly=True,  # Security feature
        secure=True,  # Use only in HTTPS
        samesite="Lax",  # Protect against CSRF
    )
    return response


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def userinfo(request):
    """
    Retrieve user information based on the provided refresh token.
    Args:
        request (Request): The HTTP request object containing the refresh token in the request data.
    Returns:
        Response: A Response object containing the user information if the refresh token is valid,
                  or an error message if the refresh token is missing or invalid.
    Raises:
        Exception: If there is an error retrieving the user information.
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
        token = RefreshToken(refresh_token)
        user = User.objects.get(id=token['user_id'])
        serializer = UserSerializer(user)
        return Response(
            {
                'message': 'User info retrieved successfully.',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        loger.error('Error retrieving user info: {}'.format(str(e)))
        return Response(
            {
                'message': 'Error retrieving user info.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Generate a new access token using the provided refresh token.
    Args:
        request (Request): The HTTP request object containing the refresh token in the request data.
    Returns:
        Response: A Response object containing the new access token if the refresh token is valid,
                  or an error message if the refresh token is missing or invalid.
    Raises:
        Exception: If there is an error generating the new access token.
    """

    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        loger.error('Refresh token is required.')
        return Response(
            {
                'message': 'Refresh token is required.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        # Create un instance of the RefreshToken class using the provided refresh token
        token = RefreshToken(refresh_token)
        # Generate a new access token from the refresh token
        access_token = str(token.access_token)
        return Response(
            {
                'message': 'Access token generated successfully.',
                'access_token': access_token
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        loger.error('Error generating access token: {}'.format(str(e)))
        return Response(
            {
                'message': 'Invalid refresh token.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_account(request):
    """
    Update the account information of the authenticated user.
    This view handles the update of user account details. It accepts partial updates
    and can handle profile picture updates if provided in the request.
    Args:
        request (HttpRequest): The HTTP request object containing user data to update.
    Returns:
        Response: A DRF Response object with a success or error message and the updated user data or errors.
    Raises:
        ValidationError: If the provided data is not valid according to the serializer.
    Example:
        To update user information, send a PATCH request with the updated fields to this view.
    """

    # Get the user form acc
    user = request.user
    # Serialize the user data and set the serializer to partial
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        loger.error('User update failed: {}.'.format(serializer.errors))
        return Response(
            {
                'message': 'User update failed.',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    # Check and update the profile picture if it exists
    if 'profile_picture' in request.data:
        user.profile_picture = request.FILES['profile_picture']  # Save the image
    # Save the updated user data
    serializer.save()
    return Response(
        {
            'message': 'User updated successfully.',
            'data': serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def change_password(request):
    """
    Handle password change requests by generating and sending an OTP code to the user's email.
    Args:
        request (HttpRequest): The HTTP request object containing the user's email.
    Returns:
        Response: A response indicating whether the password reset link will be sent if the email exists.
    The function performs the following steps:
    1. Retrieves the user's email from the request data.
    2. Logs an error and returns a generic response if the email is not provided.
    3. Searches for the user with the provided email.
    4. Logs an error and returns a generic response if the user is not found.
    5. Generates an OTP code for the user.
    6. Sends the OTP code to the user's email using a Celery task.
    7. Returns a response indicating that a password reset link will be sent if the email exists.
    """

    user_email = request.data.get('email')
    if not user_email:
        loger.error('Email is required.')
        return Response(
            {
                'message': 'If an account with this email exists, a password reset link will be sent.'
            },
            status=status.HTTP_200_OK
        )

    user = User.objects.filter(email=user_email).first()
    if not user:
        loger.error('User not found.')
        return Response(
            {
                'message': 'If an account with this email exists, a password reset link will be sent.'
            },
            status=status.HTTP_200_OK
        )

    # Genarate and send the OTP code to the user's email
    OTP = user.generate_otp()
    subject = 'Password Reset Request - Your OTP Code'
    # The template_name should be the same name as the email html version and plane text version
    template_name = 'opt_code'
    # Data to be passed to the email template from the user instance
    context = {
        'opt_code': OTP,
    }
    # Recipient list should be a list of email addresses
    recipient_list = [user.email]
    attachments = None
    # Call Celery task asynchronously
    send_otp_email.delay(subject, template_name, context, recipient_list, attachments)
    return Response(
        {
            'message': 'If an account with this email exists, a password reset link will be sent.'
        },
        status=status.HTTP_200_OK
    )
