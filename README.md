# **Smart Study AI - Backend (API)**  

This is the backend API for **Smart Study AI**, built with **Django** to provide AI-driven learning assistance. 🚀📚  

## **🚀 Getting Started**  

### **📥 Clone the Repository**  
```bash
git clone https://github.com/Salam-Hackathon/backend.git
cd backend
```

### **🐍 Set Up a Virtual Environment**  
1. **Create a virtual environment:**  
   ```bash
   python -m venv venv
   ```
2. **Activate the virtual environment:**  
   - **Windows:**  
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**  
     ```bash
     source venv/bin/activate
     ```
3. **Add `venv` to `.gitignore` to prevent committing it:**  
   ```bash
   echo "venv/" >> .gitignore
   ```

4. **Install dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```

### **📂 Additional Setup**  
1. **Create a `media` folder in the `tests` directory of the `users` app:**
   ```bash
   mkdir -p users/tests/media
   ```
2. **Download the test image from Google Drive and place it in the `media` folder**


3. **Create a `.env` file in the same directory as `manage.py` and copy the contents from Google Drive:**
   

### **⚙️ Environment Variables**  
Ensure the `.env` file contains the following environment variables:
```env
SECRET_KEY=your_secret_key

DEBUG=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=your_email@example.com
REDIS_DATABASE_URL=redis://localhost:6379/0
```

### **⚙️ Run the Development Server**  
```bash
python manage.py runserver
```

### **⚙️ Run Celery Worker and Beat**  
To start the Celery worker and beat, run the following commands in separate terminal windows:
```bash
celery -A api worker --loglevel=info
celery -A api beat --loglevel=info
```

### **🧪 Running Tests**  
Testing is required before merging any new code.  
1. Run all tests with:  
   ```bash
   python manage.py test
   ```
2. If you add new features, write corresponding tests.

### **📌 Additional Notes**  
- Follow the **Django best practices** for development.  
- Keep your **dependencies updated** and documented.  
- Document new API endpoints in the project documentation.  

## **🛠️ Development Workflow**

### **🌿 Branching Strategy**  
- Use a **feature branch** for new features:  
  ```bash
  git checkout -b feature/your-feature-name
  ```
- Use a **bugfix branch** for fixes:  
  ```bash
  git checkout -b bugfix/your-bugfix-name
  ```

### **📌 Meaningful Commit Messages**  
Follow a structured commit message format:  
```
[Feature] Add AI-powered recommendation system
[Bugfix] Fix authentication issue in API
[Refactor] Optimize database queries
[Docs] Update README with setup instructions
```

### **📝 Issues & Assignments**  
- Before working on a task, create an **issue** and assign it to a team member.  
- Provide a clear description and expected outcome.  

### **🔀 Pull Requests & Code Review**  
- Always create a **Pull Request (PR)** before merging changes.  
- At least **one review** is required before merging.  
- PR title should clearly describe the change.  

### **🔗 Contributors & Collaboration**  
For team coordination, use **GitHub Issues** and **PR Reviews** to ensure code quality.  

💡 *Let’s build Smart Study AI the right way!* 🚀
