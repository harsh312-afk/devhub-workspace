import sqlite3
from app.config import DB_PATH
from app.auth import hash_password

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT CHECK(role IN ('Admin', 'Developer', 'Member')) NOT NULL DEFAULT 'Developer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create Snippets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS snippets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        code_content TEXT NOT NULL,
        language TEXT NOT NULL,
        tags TEXT,
        is_private BOOLEAN NOT NULL DEFAULT 0,
        views_count INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    # Create Bookmarks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        snippet_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, snippet_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (snippet_id) REFERENCES snippets (id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    # Seed demo data if tables are empty
    seed_demo_data_if_empty(cursor)
    conn.commit()  # Commit the seeded data
    conn.close()

def seed_demo_data_if_empty(cursor):
    # Check if we already have any users
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count > 0:
        # Demo data already seeded, skip
        return

    print("Seeding Demo Users (no existing users found)...")
    pwd = hash_password("password123")

    users = [
        ("admin", "admin@devhub.com", pwd, "Sarah Jenkins", "Admin"),
        ("harsh_dev", "dev@devhub.com", pwd, "Harsh Gautam", "Developer"),
        ("alex_member", "member@devhub.com", pwd, "Alex Rivera", "Member")
    ]

    for u in users:
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        """, u)

    cursor.execute("SELECT id FROM users WHERE email = 'admin@devhub.com'")
    admin_id = cursor.fetchone()["id"]

    cursor.execute("SELECT id FROM users WHERE email = 'dev@devhub.com'")
    dev_id = cursor.fetchone()["id"]

    cursor.execute("SELECT id FROM users WHERE email = 'member@devhub.com'")
    member_id = cursor.fetchone()["id"]

    print("Seeding Sample Code Snippets...")
    snippets = [
        (
            dev_id,
            "FastAPI JWT Custom Authentication Middleware",
            "A lightweight JWT authentication decorator and dependency for FastAPI route security without heavy external libraries.",
            """from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hmac, hashlib, base64, json, time

security = HTTPBearer()
SECRET_KEY = "super-secret-key"

def decode_jwt(token: str):
    parts = token.split(".")
    if len(parts) != 3:
        return None
    header_b64, payload_b64, sig_b64 = parts
    sig_input = f"{header_b64}.{payload_b64}".encode()
    expected_sig = base64.urlsafe_b64encode(hmac.new(SECRET_KEY.encode(), sig_input, hashlib.sha256).digest()).decode().rstrip("=")
    if not hmac.compare_digest(sig_b64, expected_sig):
        return None
    payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "==").decode())
    if payload.get("exp", 0) < time.time():
        return None
    return payload

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    payload = decode_jwt(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload""",
            "python",
            "fastapi, jwt, security, python",
            0,
            24
        ),
        (
            dev_id,
            "Responsive Glassmorphism Card CSS",
            "Modern backdrop blur and translucent border styling for dark mode dashboards.",
            """.glass-card {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.glass-card:hover {
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 10px 30px -10px rgba(79, 70, 229, 0.2);
}""",
            "css",
            "css, styling, glassmorphism, UI",
            0,
            18
        ),
        (
            admin_id,
            "Optimized SQLite Database Connection Pool",
            "Helper pattern for managing SQLite connections with thread safety and dictionary row mapping.",
            """import sqlite3
import os

DB_PATH = "app.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn""",
            "python",
            "sqlite, database, python, backend",
            0,
            12
        ),
        (
            member_id,
            "Docker Compose Multi-Container Web Setup",
            "Production-ready docker-compose configuration for FastAPI backend and PostgreSQL database.",
            """version: '3.8'

services:
  web:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/devhub
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: devhub
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:""",
            "docker",
            "docker, postgresql, fastapi, devops",
            0,
            31
        ),
        (
            dev_id,
            "Vanilla JS Debounce Function",
            "Essential utility function for debouncing search input events to reduce unnecessary API calls.",
            """function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}""",
            "javascript",
            "javascript, webdev, performance, utility",
            1,  # Private snippet
            5
        )
    ]

    for snip in snippets:
        cursor.execute("""
            INSERT INTO snippets (user_id, title, description, code_content, language, tags, is_private, views_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, snip)

    cursor.execute("SELECT id FROM snippets WHERE title LIKE '%FastAPI%'")
    s1_id = cursor.fetchone()["id"]

    cursor.execute("SELECT id FROM snippets WHERE title LIKE '%Docker%'")
    s2_id = cursor.fetchone()["id"]

    print("Seeding Bookmarks...")
    cursor.execute("INSERT INTO bookmarks (user_id, snippet_id) VALUES (?, ?)", (dev_id, s1_id))
    cursor.execute("INSERT INTO bookmarks (user_id, snippet_id) VALUES (?, ?)", (dev_id, s2_id))

    print("Database seeding completed successfully!")