from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str
    password: str = Field(..., min_length=6)
    full_name: str
    role: Optional[str] = "Developer"

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    email: str
    full_name: str
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    created_at: str

class SnippetCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: Optional[str] = ""
    code_content: str = Field(..., min_length=1)
    language: str = Field(..., min_length=1)
    tags: Optional[str] = ""
    is_private: bool = False

class SnippetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    code_content: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[str] = None
    is_private: Optional[bool] = None

class BookmarkToggleResponse(BaseModel):
    message: str
    is_bookmarked: bool
    snippet_id: int
