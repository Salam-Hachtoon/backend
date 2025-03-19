"""
This module is responsible for makeing adapter for Google OAuth API.
- manual: https://developers.google.com/identity/protocols/oauth2/web-server
- manual: https://developers.google.com/identity/protocols/oauth2/scopes
- manual: https://developers.google.com/identity/protocols/oauth2/openid-connect


handling the Google Api by making manual requests to the Google OAuth API.
steps:
   >> front -> redircet user to Google OAuth API
    once user is authenticated, Google OAuth API will redirect user back to the front-end
    redirct the request to the backend >> callback URl
    >> backend -> make request to Google OAuth API and exchange the code for access token
    >> backend -> make request to Google OAuth API and exchange the access token for user info
    >> backend -> create user in the database if not exist
    >> backend -> return JWT tokens to the front-end

    -- functions:
        callback(request)
        extange_code_for_token(code)
        exchange_token_for_user_info(token)
   """


import requests
from api.settings import GOOGLE_REDIRECT_URI, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
import logging



def exchange_code_for_token(code):
    """
    Exchange the authorization code for an access token.
    Args:
        code (str): The authorization code received from the Google OAuth API.
    Returns:
        return: JSON response containing the access token.
    """
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        logging.error(f"Failed to exchange code for token: {response.json()}")
        return None
           
    return response.json()


def exchange_token_for_user_info(token):
    """
    Exchange the access token for the user's information.
    Args:
        token (str): The access token received from the Google OAuth API.
    Returns:
        return: JSON response containing the user's information.
    """
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(user_info_url, headers=headers)

    if response.status_code != 200:
        logging.error(f"Failed to exchange token for user info: {response.json()}")
        return None
    return response.json()
