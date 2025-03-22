# **User Authentication API Documentation**
This document provides an overview of the API endpoints available for user authentication and management. Each section includes the method, request parameters, expected responses, and status codes.

---

## **1. Signup**
### **Endpoint:**  
`POST /api/signup/`

### **Description:**  
Registers a new user.

### **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

### **Responses:**
- **201 Created**
  ```json
  {
    "message": "User created successfully.",
    "data": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
  ```
- **400 Bad Request** (User already exists)
  ```json
  {
    "message": "User already exists."
  }
  ```
- **400 Bad Request** (Validation errors)
  ```json
  {
    "message": "User creation failed.",
    "errors": {
      "email": ["This field is required."]
    }
  }
  ```

---

## **2. Signin**
### **Endpoint:**  
`POST /api/signin/`

### **Description:**  
Logs in an existing user and returns an access token.

### **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### **Responses:**
- **200 OK**
  ```json
  {
    "message": "Login successful.",
    "access_token": "jwt_access_token"
  }
  ```
  *A refresh token is set as an HTTP-only cookie.*

- **400 Bad Request** (Invalid credentials)
  ```json
  {
    "message": "Invalid credentials."
  }
  ```
- **400 Bad Request** (Missing fields)
  ```json
  {
    "message": "Email and password are required."
  }
  ```

---

## **3. Signout**
### **Endpoint:**  
`POST /api/signout/`

### **Description:**  
Logs out a user by blacklisting the refresh token.

### **Request Body:**
```json
{
  "refresh_token": "jwt_refresh_token"
}
```

### **Responses:**
- **200 OK**
  ```json
  {
    "message": "Logout successful."
  }
  ```
- **400 Bad Request** (Missing token)
  ```json
  {
    "message": "Refresh token is required."
  }
  ```
- **400 Bad Request** (Invalid token)
  ```json
  {
    "message": "Error logging out."
  }
  ```

---

## **4. User Info**
### **Endpoint:**  
`POST /api/userinfo/`

### **Description:**  
Retrieves information about the authenticated user.

### **Request Body:**
```json
{
  "refresh_token": "jwt_refresh_token"
}
```

### **Responses:**
- **200 OK**
  ```json
  {
    "message": "User info retrieved successfully.",
    "data": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
  ```
- **400 Bad Request** (Missing token)
  ```json
  {
    "message": "Refresh token is required."
  }
  ```
- **400 Bad Request** (Invalid token)
  ```json
  {
    "message": "Error retrieving user info."
  }
  ```

---

## **5. Refresh Token**
### **Endpoint:**  
`POST /api/refresh_token/`

### **Description:**  
Generates a new access token using a valid refresh token.

### **Request:**  
No request body needed. The refresh token must be stored in cookies.

### **Responses:**
- **200 OK**
  ```json
  {
    "message": "Access token generated successfully.",
    "access_token": "new_jwt_access_token"
  }
  ```
- **400 Bad Request** (Missing or invalid token)
  ```json
  {
    "message": "Refresh token is required."
  }
  ```
  ```json
  {
    "message": "Invalid refresh token."
  }
  ```

---

## **6. Update Account**
### **Endpoint:**  
`PUT /api/update_account/`

### **Description:**  
Updates the authenticated user's account details.

### **Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "profile_picture": "uploaded_image_file"
}
```
*Profile picture should be uploaded as a file.*

### **Responses:**
- **200 OK**
  ```json
  {
    "message": "User updated successfully.",
    "data": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "Jane",
      "last_name": "Doe"
    }
  }
  ```
- **400 Bad Request** (Validation errors)
  ```json
  {
    "message": "User update failed.",
    "errors": {
      "first_name": ["This field cannot be blank."]
    }
  }
  ```

---

## **7. Change Password (Send OTP)**
### **Endpoint:**  
`POST /api/change_password/`

### **Description:**  
Sends an OTP to the user's email for password reset.

### **Request Body:**
```json
{
  "email": "user@example.com"
}
```

### **Responses:**
- **200 OK** (Even if the email does not exist, for security reasons)
  ```json
  {
    "message": "If an account with this email exists, a password reset link will be sent."
  }
  ```

---

## **8. Verify OTP**
### **Endpoint:**  
`POST /api/verify_otp/`

### **Description:**  
Verifies the OTP code sent to the user's email.

### **Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

### **Responses:**
- **200 OK** (OTP is correct)
  ```json
  {
    "message": "OTP verified successfully.",
    "access_token": "new_jwt_access_token"
  }
  ```
- **400 Bad Request** (Invalid or expired OTP)
  ```json
  {
    "message": "Invalid OTP code."
  }
  ```

---

## **9. Reset Password**
### **Endpoint:**  
`POST /api/reset_password/`

### **Description:**  
Resets the user's password after OTP verification.

### **Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "NewSecurePassword123"
}
```

### **Responses:**
- **200 OK**
  ```json
  {
    "message": "Password reset successful."
  }
  ```
- **400 Bad Request** (Invalid OTP or weak password)
  ```json
  {
    "message": "Password reset failed.",
    "errors": {
      "new_password": ["Password is too weak."]
    }
  }
  ```

---

## **Authentication Flow:**
1. **User Signup (`/api/signup/`)** → Registers a user.
2. **User Signin (`/api/signin/`)** → Logs in and receives an access token.
3. **Use Access Token for Authenticated Requests** (e.g., `/api/userinfo/`).
4. **Token Refresh (`/api/refresh_token/`)** → Generates a new access token.
5. **User Logout (`/api/signout/`)** → Revokes the refresh token.
