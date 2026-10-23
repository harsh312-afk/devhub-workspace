# DevHub Workspace - Intermediate Full-Stack Web Application

**DevHub Workspace** is an enterprise-ready, intermediate-level full-stack developer knowledge hub and code snippet management platform. Built using **FastAPI**, **SQLite3**, **Tailwind CSS**, and **Vanilla JavaScript ES6**, this single-page application (SPA) allows developers and teams to create, organize, bookmark, search, fork, download, and manage code snippets with secure token-based authentication and role-based access control (RBAC).

---

## 🚀 Key Features

### 🔐 1. Authentication & Security
- **Secure Registration & Login**: Custom JWT implementation signed with HMAC-SHA256 and salted PBKDF2-HMAC-SHA256 password hashing.
- **Privilege Escalation Protection**: Public self-registration enforces `Developer` or `Member` roles; administrative privileges cannot be self-assigned.
- **Role-Based Access Control (RBAC)**: Supports `Admin`, `Developer`, and `Member` user roles.
- **Protected Routes**: Middleware authorization enforcing ownership checks on snippet editing, deletion, and privacy viewing.

### 💻 2. Code Snippet Management
- **Full CRUD Operations**: Create, read, edit, and delete snippets.
- **Privacy Controls**: Toggle between public snippets (community accessible) and private snippets (author-only / admin accessible).
- **Rich Snippet Detail Inspector**: Click any snippet to open a detailed inspection modal featuring line counts, author profile, timestamp, and formatted view.
- **Syntax Highlighting**: Beautiful code styling powered by Prism.js Tomorrow Night theme with automated language detection.
- **One-Click Code Copy**: Integrated clipboard API with instant visual confirmation toasts.
- **One-Click File Download**: Export snippets directly to local disk with the appropriate file extension (`.py`, `.js`, `.ts`, `.sql`, `.rs`, `.go`, etc.).
- **Snippet Forking**: Duplicate public snippets into your personal collection with a single click.
- **Multi-Language Support**: Categorize snippets across Python, JavaScript, TypeScript, HTML, CSS, SQL, Docker, Bash, C++, Rust, Go, JSON, YAML, and more.

### 🔖 3. Interactive Bookmarks & Engagement
- **Toggle Bookmarks**: Save essential code references to personal bookmark lists.
- **View Counter**: Accurate view tracking updated only on authorized snippet inspections.
- **Tag Filtering**: Instant click-to-filter on tags to explore matching code solutions.

### 📊 4. Search, Filtering & Dashboard
- **Instant Multi-Field Search**: Real-time debounced search matching titles, descriptions, code content, and tags.
- **Language Filtering**: Filter code cards dynamically by programming language.
- **Role-Based Analytics Dashboard**: High-level metrics showing total accessible snippets, personal snippets, saved bookmarks, and view stats.
- **1-Click Instant Demo Login**: Test different user roles instantly without manual credential entry.

---

## 🛠️ System Architecture & Tech Stack

- **Backend Framework**: Python 3.11+, FastAPI, Uvicorn ASGI Server
- **Database**: SQLite3 with foreign keys enforced on every connection, WAL mode concurrency, and cascading deletes
- **Authentication**: JWT (JSON Web Tokens) with PBKDF2-HMAC-SHA256 password hashing
- **Frontend**: Responsive dark-mode SPA built with HTML5, Tailwind CSS, Prism.js, and Vanilla JavaScript (Fetch API)
- **Deployment**: Configured for Vercel Serverless / Vercel Services via `vercel.json` and local execution via `run.py`
- **Testing**: Automated unit tests using `unittest` and FastAPI `TestClient` (14 comprehensive test cases)

---

## 📁 Project Directory Structure

```
dev_hub_workspace/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point, healthcheck & static file routing
│   ├── config.py          # Environment variables & runtime constants
│   ├── database.py        # SQLite schema initialization, connection pool & WAL config
│   ├── auth.py            # Password hashing & JWT token verification helpers
│   ├── schemas.py         # Pydantic data validation models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py        # /api/auth endpoints (register, login, me)
│   │   ├── snippets.py    # /api/snippets CRUD, filtering, search, raw & fork endpoints
│   │   ├── bookmarks.py   # /api/bookmarks toggle & retrieval endpoints
│   │   └── dashboard.py   # /api/dashboard statistics & metrics
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css  # Custom CSS extensions, theme rules & Prism overrides
│   │   └── js/
│   │       └── app.js     # Single Page Application controller, modal & API fetch handler
│   └── templates/
│       └── index.html     # Responsive Single Page Application HTML layout
├── tests/
│   ├── __init__.py
│   └── test_devhub.py     # Automated unit test suite (14 tests)
├── seed.py                # Database seeder with sample data
├── run.py                 # Application launcher
├── vercel.json            # Vercel deployment specification
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

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
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
| **Developer** | `dev@devhub.com` | `password123` | Manage personal snippets, bookmark items, fork, view analytics |
| **Member** | `member@devhub.com` | `password123` | Community view, bookmarking, personal code storage |

*(Tip: In the web interface, click on any role under **"⚡ 1-Click Instant Demo Login"** to sign in immediately!)*

---

## 📚 REST API Endpoint Documentation

### 🏥 System API
- `GET /api/health` - Healthcheck endpoint reporting service status and version

### 🔐 Authentication API
- `POST /api/auth/register` - Create a new user account & receive JWT token
- `POST /api/auth/login` - Authenticate existing credentials & issue JWT token
- `GET /api/auth/me` - Fetch profile details of authenticated user

### 💻 Snippet Management API
- `GET /api/snippets` - List public/accessible snippets (Query params: `query`, `language`, `tag`, `my_snippets`)
- `POST /api/snippets` - Create a new code snippet
- `GET /api/snippets/{id}` - Fetch detailed snippet & increment view counter
- `GET /api/snippets/{id}/raw` - Download raw code text
- `POST /api/snippets/{id}/fork` - Fork snippet to current user's workspace
- `PUT /api/snippets/{id}` - Update existing snippet (Author or Admin)
- `DELETE /api/snippets/{id}` - Delete snippet (Author or Admin)

### 🔖 Bookmarks API
- `POST /api/bookmarks/{id}/toggle` - Toggle bookmark status for a snippet
- `GET /api/bookmarks` - List all snippets bookmarked by the current user

### 📊 Dashboard API
- `GET /api/dashboard/stats` - Fetch real-time usage statistics and language distribution

---

## 🌐 Deploying to Vercel

DevHub Workspace includes native configuration for Vercel deployment:

```bash
# Link project to Vercel
vercel link --yes

# Deploy to Production
vercel --prod
```

---

## 🧪 Running Unit Tests

Run the automated test suite covering all security, CRUD, and access control behaviors:

```bash
python3 tests/test_devhub.py
```
