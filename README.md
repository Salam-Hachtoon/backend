# **Smart Study AI - Backend (API)**  

This is the backend API for **Smart Study AI**, built with **Django** to provide AI-driven learning assistance. 🚀📚  

## **🚀 Getting Started**  

### **📥 Clone the Repository**  
```bash
git clone https://github.com/Salam-Hachtoon/API.git
cd API
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

### **⚙️ Run the Development Server**  
```bash
python manage.py runserver
```

---

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

---

## **🧪 Running Tests**  
Testing is required before merging any new code.  
1. Run all tests with:  
   ```bash
   python manage.py test
   ```
2. If you add new features, write corresponding tests.  

---

## **📌 Additional Notes**  
- Follow the **Django best practices** for development.  
- Keep your **dependencies updated** and documented.  
- Document new API endpoints in the project documentation.  

---

### **🔗 Contributors & Collaboration**  
For team coordination, use **GitHub Issues** and **PR Reviews** to ensure code quality.  

💡 *Let’s build Smart Study AI the right way!* 🚀
