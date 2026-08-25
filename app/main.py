import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, snippets, bookmarks, dashboard

# Initialize database on application startup
init_db()

app = FastAPI(
    title="DevHub Workspace API",
    description="Full-stack Developer Knowledge Hub & Snippet Management Platform",
    version="1.0.0"
)

# Enable CORS for flexible integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Register API Routers
app.include_router(auth.router)
app.include_router(snippets.router)
app.include_router(bookmarks.router)
app.include_router(dashboard.router)

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    # Serve the HTML template directly to avoid Jinja2 template caching issues
    template_path = os.path.join(BASE_DIR, "templates", "index.html")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Template not found</h1>", status_code=404)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading template: {str(e)}</h1>", status_code=500)