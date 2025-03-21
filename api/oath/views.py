import requests, logging
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from rest_framework.permissions import AllowAny # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from rest_framework.decorators import api_view, permission_classes # type: ignore
from django.conf import settings
from django.shortcuts import redirect
from ..users.serializers import UserSerializer
from .utility import generate_jwt_tokens

# Create the looger instance for the celery tasks
loger = logging.getLogger('requests')

# Get the user model
User = get_user_model()



def google_login(request):
    """
    Redirect user to Google's OAuth 2.0 authentication page.
    """
    google_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri=http://127.0.0.1:8000/api/auth/google/callback/"
        "&scope=email%20profile"
    )
    return redirect(google_url)



@api_view(['GET'])
@permission_classes([AllowAny])
def google_callback(request):
    # Get the code from the query parameters
    code = request.GET.get("code")

    # Check if code is provided
    if not code:
        loger.error("No code provided")
        return Response(
            {
                "message": "No code provided"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get the access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://127.0.0.1:8000/api/auth/google/callback/",
    }

    token_response = requests.post(token_url, data=token_data).json()
    access_token = token_response.get("access_token")

    if not access_token:
        loger.error("Failed to obtain access token")
        return Response(
            {
                "message": "Failed to obtain access token"
            }
            , status=status.HTTP_400_BAD_REQUEST
        )

    # Fetch user info
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    user_info = requests.get(
        user_info_url,
        headers={
            "Authorization": "Bearer {}".format(access_token)
        }
    ).json()

    email = user_info.get("email")
    first_name = user_info.get("given_name")
    last_name = user_info.get("family_name")
    profile_picture = user_info.get("picture")

    if not email:
        loger.error("Failed to retrieve email")
        return Response(
            {
                "message": "Failed to retrieve email"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if user exists or create a new one
    user, created = User.objects.get_or_create(email=email, defaults={
        "first_name": first_name,
        "last_name": last_name,
    })

    # Update user profile picture
    if created:
        user.profile.picture = profile_picture  # Assuming a user profile exists

    user.save()

    # Generate JWT Token
    access_token, refresh_token = generate_jwt_tokens(user)

    # Serialize the user data
    user_serializer = UserSerializer(user)

    response = Response(
        {
            'message': 'Login successful.',
            'user': user_serializer.data,
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
