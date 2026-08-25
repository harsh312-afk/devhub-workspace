# DevHub Workspace - Intermediate Full-Stack Web Application

**DevHub Workspace** is an enterprise-ready, intermediate-level full-stack developer knowledge hub and code snippet management platform. Built using **FastAPI**, **SQLite3**, **Tailwind CSS**, and **Vanilla JavaScript ES6**, this single-page application (SPA) allows developers and teams to create, organize, bookmark, search, and manage code snippets with secure token-based authentication and role-based access control (RBAC).

---

## 🚀 Key Features

### 🔐 1. Authentication & Security
- **Secure Registration & Login**: Custom JWT implementation signed with HMAC-SHA256 and salted PBKDF2 password hashing.
- **Role-Based Access Control (RBAC)**: Supports `Admin`, `Developer`, and `Member` user roles.
- **Protected Routes**: Middleware authorization enforcing ownership checks on snippet editing and deletion.

### 💻 2. Code Snippet Management
- **Full CRUD Operations**: Create, read, edit, and delete snippets.
- **Privacy Controls**: Toggle between public snippets (community accessible) and private snippets (author-only).
- **One-Click Code Copy**: Integrated clipboard API integration with visual confirmation toasts.
- **Syntax & Language Support**: Categorize snippets across Python, JavaScript, HTML, CSS, SQL, Docker, Bash, C++, and more.

### 🔖 3. Interactive Bookmarks & Engagement
- **Toggle Bookmarks**: Save essential code references to personal bookmark lists.
- **Analytics Tracking**: Real-time counter for snippet view counts and community engagement metrics.

### 📊 4. Search, Filtering & Dashboard
- **Instant Multi-Field Search**: Real-time debounced search matching titles, descriptions, code content, and tags.
- **Language Filtering**: Filter code cards by programming language.
- **Role-Based Analytics Dashboard**: High-level metrics showing total accessible snippets, personal snippets, saved bookmarks, and view stats.

---

## 🛠️ System Architecture & Tech Stack

- **Backend Framework**: Python 3.11, FastAPI, Uvicorn ASGI Server
- **Database**: SQLite3 (`devhub.db`) with foreign key constraints & cascading deletes
- **Authentication**: JWT (JSON Web Tokens) with PBKDF2-HMAC-SHA256 password hashing
- **Frontend**: Responsive SPA built with HTML5, Tailwind CSS, and Vanilla JavaScript (Fetch API & DOM Controller)
- **Testing**: Automated unit tests using `unittest` and FastAPI `TestClient`

---

## 📁 Project Directory Structure

```
dev_hub_workspace/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point & static file routing
│   ├── config.py          # Environment variables & runtime constants
│   ├── database.py        # SQLite schema initialization & connection pool
│   ├── auth.py            # Password hashing & JWT token verification helpers
│   ├── schemas.py         # Pydantic data validation models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py        # /api/auth endpoints (register, login, me)
│   │   ├── snippets.py    # /api/snippets CRUD, filtering & search endpoints
│   │   ├── bookmarks.py   # /api/bookmarks toggle & retrieval endpoints
│   │   └── dashboard.py   # /api/dashboard statistics & metrics
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css  # Custom CSS extensions & theme rules
│   │   └── js/
│   │       └── app.js     # Single Page Application controller & API fetch handler
│   └── templates/
│       └── index.html     # Responsive Single Page Application HTML layout
├── tests/
│   ├── __init__.py
│   └── test_devhub.py     # Automated unit test suite
├── seed.py                # Database seeder with sample data
├── run.py                 # Application launcher
├── requirements.txt       # Project dependencies manifest
└── README.md              # Project documentation & API guide
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.8 or higher installed on your system.

### 2. Installation & Setup
```bash
# Clone or navigate to the project directory
cd dev_hub_workspace

# Install dependencies
pip install -r requirements.txt

# Seed the database with initial demo users and snippets
python3 seed.py

# Launch the development server
python3 run.py
```

Open your web browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🔑 Demo Credentials

| Role | Email Address | Password | Permissions & Access Scope |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@devhub.com` | `password123` | Full administrative management across all snippets |
| **Developer** | `dev@devhub.com` | `password123` | Manage personal snippets, bookmark items, view analytics |
| **Member** | `member@devhub.com` | `password123` | Community view, bookmarking, personal code storage |

---

## 📚 REST API Endpoint Documentation

### 🔐 Authentication API
- `POST /api/auth/register` - Create a new user account & receive JWT token
- `POST /api/auth/login` - Authenticate existing credentials & issue JWT token
- `GET /api/auth/me` - Fetch profile details of authenticated user

### 💻 Snippet Management API
- `GET /api/snippets` - List public/accessible snippets (Query params: `query`, `language`, `tag`, `my_snippets`)
- `POST /api/snippets` - Create a new code snippet
- `GET /api/snippets/{id}` - Fetch detailed snippet & increment view counter
- `PUT /api/snippets/{id}` - Update existing snippet (Author or Admin)
- `DELETE /api/snippets/{id}` - Delete snippet (Author or Admin)

### 🔖 Bookmarks API
- `POST /api/bookmarks/{id}/toggle` - Toggle bookmark status for a snippet
- `GET /api/bookmarks` - List all snippets bookmarked by the current user

### 📊 Dashboard API
- `GET /api/dashboard/stats` - Fetch real-time usage statistics and language distribution

---

## 🧪 Running Unit Tests

Run the automated test suite to verify route handlers and security rules:

```bash
python3 tests/test_devhub.py
```
