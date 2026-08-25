from fastapi import APIRouter, HTTPException, status, Depends
from app.database import get_db_connection
from app.auth import verify_password, hash_password, create_access_token, get_current_user
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
def register(user_data: RegisterRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if username or email exists
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (user_data.email, user_data.username))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username or Email already registered")

    hashed_pwd = hash_password(user_data.password)
    role_flag = user_data.role if user_data.role in ['Admin', 'Developer', 'Member'] else 'Developer'

    cursor.execute("""
        INSERT INTO users (username, email, hashed_password, full_name, role)
        VALUES (?, ?, ?, ?, ?)
    """, (user_data.username, user_data.email, hashed_pwd, user_data.full_name, role_flag))

    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    token_payload = {
        "user_id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": role_flag
    }

    access_token = create_access_token(token_payload)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user_id,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=role_flag
    )

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (credentials.email,))
    user = cursor.fetchone()

    # Debug logging to help troubleshoot login issues
    if not user:
        print(f"LOGIN DEBUG: No user found for email: {credentials.email}")
    else:
        print(f"LOGIN DEBUG: User found for email: {credentials.email}, checking password...")
        password_match = verify_password(credentials.password, user["hashed_password"])
        print(f"LOGIN DEBUG: Password match result: {password_match}")
        if not password_match:
            print(f"LOGIN DEBUG: Password verification failed for email: {credentials.email}")

    conn.close()

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token_payload = {
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"]
    }

    access_token = create_access_token(token_payload)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"]
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, full_name, role, created_at FROM users WHERE id = ?", (current_user["user_id"],))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return dict(user)