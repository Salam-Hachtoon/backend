# API Documentation for Endpoints

This document describes the API endpoints for handling file uploads, generating summaries, creating flashcards, and generating quizzes. It provides details on the required inputs, expected responses, and HTTP status codes for each endpoint.

---

## 1. Upload Attachments
**Endpoint:**  
`POST /upload_attachments/`

**Description:**  
Allows authenticated users to upload multiple file attachments (maximum of 3 files per request).

**Authentication:**  
✅ Required (Bearer Token)

**Request Headers:**
```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Request Body (Multipart Form Data):**
```
files: [File, File, File]  // Maximum 3 files
```

**Success Response:**  
**Status Code:** `201 Created`
```json
{
  "message": "Files uploaded successfully.",
  "data": [
    {
      "id": 1,
      "file": "https://example.com/media/file1.pdf",
      "status": "pending",
      "batch_id": "1712345678"
    },
    {
      "id": 2,
      "file": "https://example.com/media/file2.pdf",
      "status": "pending",
      "batch_id": "1712345678"
    }
  ]
}
```

**Error Responses:**  
- **400 Bad Request** (More than 3 files)
```json
{
  "message": "Maximum file limit exceeded. Only 3 files are allowed."
}
```
- **400 Bad Request** (Invalid file data)
```json
{
  "message": "Invalid file upload data.",
  "errors": { "<field_errors>" }
}
```

---

## 2. Generate Summary  
**Endpoint:**  
`POST /get_summary/`

**Description:**  
Generates a text summary from uploaded files based on their batch ID.

**Authentication:**  
✅ Required (Bearer Token)

**Request Headers:**
```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Request Body (JSON):**
```json
{
  "batch_id": "1712345678"
}
```

**Success Response:**  
**Status Code:** `201 Created`
```json
{
  "message": "Summary created successfully.",
  "data": {
    "id": 5,
    "content": "This is the summarized text extracted from the uploaded files."
  }
}
```

**Error Responses:**  
- **400 Bad Request** (Batch ID not provided)
```json
{
  "message": "Batch ID not provided."
}
```
- **404 Not Found** (No files found for the batch)
```json
{
  "message": "No files found for batch ID: 1712345678"
}
```
- **400 Bad Request** (Files not processed yet)
```json
{
  "message": "Not all files have been processed yet."
}
```
- **500 Internal Server Error** (AI service failed)
```json
{
  "message": "Failed to generate summary."
}
```

---

## 3. Generate Flashcards  
**Endpoint:**  
`POST /get_flash_cards/`

**Description:**  
Generates flashcards based on an existing summary.

**Authentication:**  
✅ Required (Bearer Token)

**Request Headers:**
```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Request Body (JSON):**
```json
{
  "id": 5  // Summary ID
}
```

**Success Response:**  
**Status Code:** `201 Created`
```json
{
  "message": "Flashcards generated and saved successfully.",
  "data": [
    {
      "id": 1,
      "term": "Artificial Intelligence",
      "definition": "The simulation of human intelligence by machines."
    },
    {
      "id": 2,
      "term": "Machine Learning",
      "definition": "A subset of AI that enables machines to learn from data."
    }
  ]
}
```

**Error Responses:**  
- **400 Bad Request** (Summary ID not provided)
```json
{
  "message": "Summary ID not provided."
}
```
- **404 Not Found** (Summary does not exist)
```json
{
  "message": "Summary with ID 5 not found."
}
```
- **500 Internal Server Error** (AI service failed)
```json
{
  "message": "Failed to generate flash cards."
}
```

---

## 4. Generate Quiz  
**Endpoint:**  
`POST /get_quiz/`

**Description:**  
Generates a quiz based on a summary’s content and a difficulty level.

**Authentication:**  
✅ Required (Bearer Token)

**Request Headers:**
```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Request Body (JSON):**
```json
{
  "id": 5,  // Summary ID
  "difficulty": "medium"
}
```

**Success Response:**  
**Status Code:** `201 Created`
```json
{
  "message": "Quiz generated successfully.",
  "data": {
    "id": 3,
    "difficulty": "medium",
    "questions": [
      {
        "id": 10,
        "question": "What is the primary goal of AI?",
        "choices": [
          "To mimic human intelligence",
          "To store large amounts of data",
          "To replace human workers",
          "To process numbers faster"
        ],
        "correct_choice": "To mimic human intelligence"
      },
      {
        "id": 11,
        "question": "Which field is AI most commonly associated with?",
        "choices": [
          "Psychology",
          "Biology",
          "Computer Science",
          "History"
        ],
        "correct_choice": "Computer Science"
      }
    ]
  }
}
```

**Error Responses:**  
- **400 Bad Request** (Missing summary ID or difficulty level)
```json
{
  "message": "Either summary id or difficulty level not provided."
}
```
- **404 Not Found** (Summary does not exist)
```json
{
  "message": "Summary with ID 5 not found."
}
```
- **500 Internal Server Error** (AI service failed)
```json
{
  "message": "Failed to generate quiz."
}
```

---

## Notes  
1. All endpoints require an authentication token in the `Authorization` header.  
2. The AI service used for summaries, flashcards, and quizzes must be operational for these features to work.  
3. Responses follow a structured JSON format for easy integration with frontend applications.  
