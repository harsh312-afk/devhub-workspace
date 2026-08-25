import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("DEVHUB_DB_PATH", "/tmp/devhub.db")
SECRET_KEY = os.environ.get("DEVHUB_SECRET_KEY", "devhub-secure-jwt-secret-key-2026")
TOKEN_EXPIRE_SECONDS = 86400  # 24 Hours
