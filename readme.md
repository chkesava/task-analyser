# 🧠 Smart Task Analyzer

A lightweight **Django + JavaScript** web app that helps you decide **what to work on first** by analyzing and prioritizing tasks based on **due date**, **importance**, **effort**, and **dependencies**.

The app gives you:
- **`POST /api/tasks/analyze/`** → Analyze and score a list of tasks  
- **`GET /api/tasks/suggest/`** → Suggest the top 3 tasks to focus on

---

## 🚀 Tech Stack

### Backend
- Python 3.8+
- Django 4.x
- Django REST Framework

### Frontend
- HTML5, CSS3, Vanilla JavaScript

### Database
- SQLite (auto-managed by Django)

---
## 📁 Project Structure
```bash
├── backend/ # Django project
│ ├── settings.py
│ ├── urls.py
│ └── ...
├── tasks/ # Django app
│ ├── models.py
│ ├── views.py
│ ├── scoring.py
│ ├── urls.py
│ └── ...
├── frontend/ # Frontend static files
│ ├── index.html
│ ├── style.css
│ └── script.js
├── smart_task_analyzer.http # HTTP test cases
├── manage.py
├── requirements.txt
└── README.md
```

### Ignore virtual environments
- venv/
- .env
### Ignore Python bytecode and cache
- pycache/
- *.pyc
- *.pyo
- *.pyd
### Ignore local SQLite database
- db.sqlite3
### Ignore logs and temp files
- *.log
- *.tmp
### Ignore IDE/editor settings
- .vscode/
- .idea/

These files will be recreated locally after cloning.

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/chkesava/task-analyser.git
```
```bash
cd task-analyser
```


### 2️⃣ Create and Activate Virtual Environment

**Windows (PowerShell):**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations
```bash
python manage.py migrate
```
### 5️⃣ Run the Backend Server
```bash
python manage.py runserver
```

Server will start at  
👉 [**http://127.0.0.1:8000/**](http://127.0.0.1:8000/)

**APIs available:**
- `POST /api/tasks/analyze/`
- `GET /api/tasks/suggest/`

### 💻 Frontend Setup

**Option A – VS Code Live Server (Recommended)**
1. Open the project folder in VS Code
2. Install the **Live Server** extension
3. Open `frontend/index.html`
4. Right-click → **"Open with Live Server"**

This launches your frontend at:  
👉 [**http://127.0.0.1:5500/frontend/index.html**](http://127.0.0.1:5500/frontend/index.html)

**Make sure Django backend is running at the same time.**

**Option B – Open Directly**
Double-click `frontend/index.html` to open in browser,  
**but this might cause CORS errors** — Live Server is safer.

---

## 🌐 API Endpoints

### 1️⃣ `POST /api/tasks/analyze/`
Analyze and score a list of tasks.

**Example Request**
``` bash
[
  {
    "title": "Fix login issue",
    "due_date": "2025-11-30",
    "importance": 9,
    "estimated_hours": 3,
    "dependencies": []
  },
  {
    "title": "Implement search feature",
    "due_date": "2025-12-10",
    "importance": 8,
    "estimated_hours": 10,
    "dependencies": []
  },
  {
    "title": "Clean up CSS",
    "due_date": "2025-12-02",
    "importance": 5,
    "estimated_hours": 2,
    "dependencies": []
  },
  {
    "title": "Database backup setup",
    "due_date": "2025-12-01",
    "importance": 7,
    "estimated_hours": 4,
    "dependencies": []
  },
  {
    "title": "Review PRs",
    "due_date": "2025-11-29",
    "importance": 6,
    "estimated_hours": 1,
    "dependencies": []
  },
  {
    "title": "Update documentation",
    "due_date": "2025-12-05",
    "importance": 5,
    "estimated_hours": 3,
    "dependencies": []
  },
  ```
  **Example Response**
  ```bash
[
  {
    "title": "Fix login issue",
    "due_date": "2025-11-30",
    "importance": 9,
    "estimated_hours": 3,
    "dependencies": [],
    "priority_score": 105,
    "reason": "Due soon (≤3 days). Importance adds 45."
  },
  {
    "title": "Review PRs",
    "due_date": "2025-11-29",
    "importance": 6,
    "estimated_hours": 1,
    "dependencies": [],
    "priority_score": 100,
    "reason": "Due soon (≤3 days). Importance adds 30. Quick win bonus."
  },
  {
    "title": "Clean up CSS",
    "due_date": "2025-12-02",
    "importance": 5,
    "estimated_hours": 2,
    "dependencies": [],
    "priority_score": 95,
    "reason": "Due soon (≤3 days). Importance adds 25. Quick win bonus."
  },
  {
    "title": "Database backup setup",
    "due_date": "2025-12-01",
    "importance": 7,
    "estimated_hours": 4,
    "dependencies": [],
    "priority_score": 95,
    "reason": "Due soon (≤3 days). Importance adds 35."
  },
  {
    "title": "Write unit tests",
    "due_date": "2025-12-06",
    "importance": 7,
    "estimated_hours": 5,
    "dependencies": [],
    "priority_score": 75,
    "reason": "Due this week. Importance adds 35."
  },
]
```

### 2️⃣ `GET /api/tasks/suggest/`
Returns the top 3 tasks from the most recently analyzed list.

**Example Response**
```bash
[
{
"title": "Fix login bug",
"priority_score": 105,
"reason": "Due soon (≤3 days). Importance adds 40. Quick win bonus.",
"due_date": "2025-12-01",
"importance": 8,
"estimated_hours": 3,
"dependencies": []
}
]
```

**If no analysis has been run yet:**
```bash
{ "error": "No tasks analyzed yet." }
```

---

## 🧮 Backend Logic

### `/analyze/` API
- Receives a JSON list of tasks
- For each task:
  - Calculates urgency (days until due date)
  - Adds importance weight
  - Adjusts based on effort (shorter = bonus)
  - Penalizes tasks with dependencies
- Returns the **sorted list by priority_score**
- Saves the analyzed batch **in memory** (not database)

### `/suggest/` API
- Picks the **top 3 highest-scoring tasks** from the last analyzed list
- Returns them with their reasoning
- If analyze hasn't been called yet, returns an error message

---

## 🖥️ Frontend Overview

### Left Panel
- Form inputs for:
  - **Title**
  - **Due date**
  - **Importance (1–10)**
  - **Estimated hours**
  - **Dependencies (comma-separated)**
- Buttons:
  - **Add Task** → Adds to local list
  - **Analyze Tasks** → Sends to backend for scoring
  - **Get Suggestions** → Fetches top 3 from backend
- **Sorting dropdown** (Smart Balance, Fastest Wins, High Impact, Deadline Driven)
- **Status bar** for success/error messages

### Right Panel
Displays analyzed or suggested tasks with:
- Task title
- **Score**
- Due date, importance, effort
- **Color-coded priority labels** (High / Medium / Low)
- **Explanation (reason)** text

---

## 🧪 Testing APIs with `.http` File
The repo includes a `smart_task_analyzer.http` file for API testing.

**Run Tests in VS Code:**
1. Install the **REST Client** extension
2. Open `smart_task_analyzer.http`
3. Make sure backend is running
4. Click **"Send Request"** above any block

The file covers:
- Valid requests
- Missing fields
- Invalid dates
- Past due tasks
- Dependency handling
- Suggest API behavior

---

## 🧰 Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'rest_framework'` | DRF not installed | Run `pip install djangorestframework` and ensure `'rest_framework'` is in `INSTALLED_APPS` |
| CORS error in browser | Directly opening file URL | Use **VS Code Live Server** instead |
| "No tasks analyzed yet" | Suggest API called before analyze | Run `/api/tasks/analyze/` first |
| Empty frontend results | JS render timing bug | Ensure latest `script.js` version is used |
| Database error | Missing migrations | Run `python manage.py migrate` |

---

## 💾 Updating Dependencies
When you install new packages, update `requirements.txt`:

```bash
pip freeze > requirements.txt
```