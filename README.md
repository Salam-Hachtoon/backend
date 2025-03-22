# **IASQ Backend Project**

## **Description**
The IASQ Backend Project is a Django-based application that provides APIs for:
- **User Authentication**  
- **File Processing** (PDF, DOCX, TXT, PPTX)  
- **AI-powered Summarization**  
- **Flashcard Generation & Quiz Creation**  
- **Bookmarking**  

It integrates **Celery** for asynchronous task processing and uses **JWT-based authentication** for secure user sessions.

---

## **Features**

### **User Authentication**
- Signup with JWT token generation.  
- Profile image upload with validation.  
- Welcome email sent upon successful registration.  

### **File Processing**
- Supports PDF, DOCX, TXT, and PPTX file types.  
- Extracts text content from uploaded files.  
- **Now using Django Signals to automate text extraction and database updates.**  
- Tracks file processing status: `Pending`, `Processing`, `Completed`, `Failed`.  

### **AI-Powered Features**
- **Summarization:** Generates concise summaries of uploaded content.  
- **Flashcard Generation:** Creates educational flashcards based on summaries.  
- **Quiz Creation:** Generates multiple-choice quizzes from summaries.  

### **Bookmarking**
- Allows users to bookmark summaries, flashcards, and quiz questions.  

### **Asynchronous Task Processing**
- Uses **Celery** for background task execution.  
- **Redis** as the message broker.  

---

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone https://github.com/Salam-Hackathon/backend.git
cd backend
```

### **2. Set Up a Virtual Environment**
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Configure Environment Variables**
Create a `.env` file in the root directory and add:
```ini
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True
```

### **5. Run Database Migrations**
```bash
python manage.py migrate
```

### **6. Run the Development Server**
```bash
python manage.py runserver
```

### **7. Start Celery Worker and Beat**
```bash
# Go to the project dir.
cd api
# Start the Celery worker
celery -A api worker --loglevel=info

# Start the Celery beat scheduler
celery -A api beat --loglevel=info
```

### **8. Run Tests**
```bash
python manage.py test
```

---

## **API Endpoints**

### **Authentication**
#### **Signup**
**POST** `/api/auth/signup/`
##### **Request Body**
```json
{
    "email": "user@example.com",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe",
    "profile_picture": "upload a jpg/png file"
}
```
##### **Response**
- User is created successfully.  
- A JWT token is returned.  
- A welcome email is sent.  

---

### **File Processing**
#### **Upload File**
**POST** `/api/files/upload/`
- Supported File Types: `PDF, DOCX, TXT, PPTX`
##### **Response**
- File is saved, and status is updated to `processing`.  
- Text is extracted automatically using **Django Signals**.  
- Status is updated to `completed`.  

---

### **AI-Powered Features**
#### **Summarization**
**POST** `/api/ai/summarize/`
##### **Request Body**
```json
{
    "file_id": 1
}
```
##### **Response**
- Returns a summary of the file content.  

#### **Flashcard Generation**
**POST** `/api/ai/flashcards/`
##### **Request Body**
```json
{
    "summary_id": 1
}
```
##### **Response**
- Generates flashcards based on the summary.  

#### **Quiz Creation**
**POST** `/api/ai/quiz/`
##### **Request Body**
```json
{
    "summary_id": 1,
    "difficulty": "medium"
}
```
##### **Response**
- Creates a quiz with multiple-choice questions.  

---

### **Bookmarking**
#### **Create Bookmark**
**POST** `/api/bookmarks/create/`
##### **Request Body**
```json
{
    "object_id": 1,
    "model_name": "summary"
}
```
##### **Response**
- Bookmark is created successfully.  

#### **List Bookmarks**
**GET** `/api/bookmarks/`
##### **Response**
- Returns all bookmarks for the authenticated user.  

---

## **Testing the Application**
### **Run Unit Tests**
```bash
python manage.py test
```
### **Verify API Endpoints**
- Use **Postman** or **cURL** to test API requests.  

### **Check Logs**
- Logs are stored in the `logs/` directory for debugging.  

---

## **Next Steps**
✅ Implement user login functionality.  
✅ Add a profile update endpoint.  
✅ Write unit tests for all endpoints.  
✅ Enhance error handling and logging.  

---

## **Contributors**
- **Ibrahim Hanafi Mohamed** ([hfibrahim90@gmail.com](mailto:hfibrahim90@gmail.com))  
- **Mahmoud Adam** ([mahmoudadam5555@gmail.com](mailto:mahmoudadam5555@gmail.com))  

---

### **Changes in This Update:**
- **Removed hashing tables for file tracking.**
- **Replaced with Django Signals for automatic text extraction and database updates.**
- **Updated README structure for better readability.**
