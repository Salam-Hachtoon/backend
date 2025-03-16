### **Title:** ✨ Implement User Signup with JWT, Profile Image & Welcome Email  

### **Description:**  
This PR adds the **user signup API endpoint**, integrating **JWT authentication**, **profile image upload**, and sending a **welcome email** upon successful registration. It also includes setup instructions for configuring the server.  

### **Key Changes:**  
- Implemented **user signup API endpoint** with JWT authentication.  
- Added **profile image upload** functionality.  
- Configured validation for **profile image (jpg, jpeg, png) with a max size of 5MB**.  
- Implemented **welcome email** after successful signup.  
- Updated **README** with **server setup instructions**.  

### **How to Test:**  
**Clone the Repository:**
`git clone https://github.com/Salam-Hackathon/backend.git
cd backend`

### **Set Up a Virtual Environment:**

1. Create a virtual environment:**
`python -m venv venv`
**Activate the virtual environment:**
**Windows:**
`venv\Scripts\activate`
**macOS/Linux:**
`source venv/bin/activate`

2. **Install Dependencies:**
`pip install -r requirements.txt`

3. **Additional Setup:**

4. **Create a media folder in the tests directory of the users app:**
`mkdir -p users/tests/media`
 - Download the test image from Google Drive and place it in the media folder.
 - Create a .env file in the same directory as manage.py and copy the contents from Google Drive.

5. **Run the Development Server:**
`python manage.py runserver`

6. **Run Celery Worker and Beat:**
**Start the Celery worker:**
`celery -A api worker --loglevel=info`
**Start the Celery beat:**
`celery -A api beat --loglevel=info`

7. **Run Tests:**
'python manage.py test'

8. Make a **POST** request to the signup endpoint:  
   ```
   POST /api/auth/signup/  
   Content-Type: multipart/form-data  
   ```  
   **Sample Request Body:**  
   ```json
   {
       "email": "user@example.com",
       "password": "securepassword",
       "first_name": "John",
       "last_name": "Doe",
       "profile_picture": "upload a jpg/png file"
   }
   ```  
4. Check if:  
   - The **user is created** successfully.  
   - A **JWT token** is returned.  
   - The **profile image is stored** correctly.  
   - A **welcome email** is received.  

### **Next Steps:**  
- Implement user login.  
- Add profile update endpoint.  
- Write unit tests for authentication endpoints.  
