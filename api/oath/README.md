# API Documentation: Google OAuth2 Authentication

This document outlines the authentication endpoints for Google OAuth2 login, providing details on how to call them, required parameters, expected responses, and status codes.

---

## **1. Google Login Endpoint**
### **Endpoint:**  
`GET /api/auth/google/login/`

### **Description:**  
Redirects the user to Google's OAuth2 authentication page, where they can log in and grant access.

### **Request Parameters:**  
No request parameters required.

### **Response:**  
Redirects to Google's authentication page.

### **Status Codes:**  
- `302 Found` – Redirects to Google OAuth2 authentication.

### **Example Request:**
```http
GET http://127.0.0.1:8000/api/auth/google/login/
```

---

## **2. Google OAuth2 Callback Endpoint**
### **Endpoint:**  
`GET /api/auth/google/callback/`

### **Description:**  
Handles the OAuth2 callback after the user logs in via Google. It retrieves the authorization code, exchanges it for an access token, fetches user information, and returns JWT tokens.

### **Request Parameters:**  
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | `string` | Yes | Authorization code returned by Google after successful login. |

### **Expected Responses:**

#### **1. Success Response**
- **Status Code:** `200 OK`
- **Response Body:**
```json
{
    "message": "Login successful.",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "profile_picture": "https://example.com/profile.jpg"
    },
    "access_token": "your_access_token"
}
```
- **Cookies Set:**
  - `refresh_token` (HTTP-only, secure)

#### **2. Error Responses**
| Status Code | Error Message | Cause |
|-------------|--------------|-------|
| `400 Bad Request` | `{ "message": "No code provided" }` | Missing `code` parameter. |
| `400 Bad Request` | `{ "message": "Failed to obtain access token" }` | Invalid or expired authorization code. |
| `400 Bad Request` | `{ "message": "Failed to retrieve email" }` | Google API did not return an email. |

### **Example Requests:**

#### **1. Successful Login**
```http
GET http://127.0.0.1:8000/api/auth/google/callback/?code=AUTHORIZATION_CODE
```

#### **2. Error Cases**
```http
GET http://127.0.0.1:8000/api/auth/google/callback/?code=INVALID_CODE
```
_Response:_
```json
{
    "message": "Failed to obtain access token"
}
```

---

## **Usage Notes**
- The `access_token` should be included in the `Authorization` header (`Bearer access_token`) for authenticated requests.
- The `refresh_token` is stored as an HTTP-only cookie and cannot be accessed via JavaScript.
- Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are configured in Django settings.
- The `redirect_uri` should match the one configured in the Google API Console.
