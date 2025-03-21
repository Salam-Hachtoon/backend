import requests
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse



def google_login(request):
    """
    Redirect user to Google's OAuth 2.0 authentication page.
    """
    google_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        f"&client_id={settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']}"
        f"&redirect_uri=http://127.0.0.1:8000/api/auth/google/callback/"
        "&scope=email%20profile"
    )
    return redirect(google_url)



def google_callback(request):
    """
    Exchange authorization code for an access token and retrieve user info.
    """
    code = request.GET.get("code")

    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"],
        "client_secret": settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["secret"],
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://127.0.0.1:8000/api/auth/google/callback/",
    }

    # Get access token
    token_response = requests.post(token_url, data=token_data).json()
    access_token = token_response.get("access_token")

    if not access_token:
        return JsonResponse({"error": "Failed to obtain access token"}, status=400)

    # Fetch user info
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    user_info = requests.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"}).json()

    email = user_info.get("email")
    first_name = user_info.get("given_name", "")
    last_name = user_info.get("family_name", "")
    profile_picture = user_info.get("picture")

    if not email:
        return JsonResponse({"error": "Failed to retrieve email"}, status=400)

    # Check if user exists or create a new one
    from ..users.models import User
    user, created = User.objects.get_or_create(email=email, defaults={"first_name": first_name, "last_name": last_name})

    # Update profile picture if not set
    if created:
        user.profile.picture = profile_picture  # Assuming `profile.picture` exists

    user.save()

    return JsonResponse({
        "message": "Login successful",
        "user": {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_picture": profile_picture,
        }
    })
