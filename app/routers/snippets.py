from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional, List
from datetime import datetime
from app.database import get_db_connection
from app.auth import get_current_user
from app.schemas import SnippetCreate, SnippetUpdate

router = APIRouter(prefix="/api/snippets", tags=["Snippets"])

@router.get("")
def list_snippets(
    query: Optional[str] = None,
    language: Optional[str] = None,
    tag: Optional[str] = None,
    my_snippets: Optional[bool] = False,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = """
        SELECT s.*, u.full_name as author_name, u.username as author_username,
               (SELECT COUNT(*) FROM bookmarks b WHERE b.snippet_id = s.id AND b.user_id = ?) as is_bookmarked
        FROM snippets s
        JOIN users u ON s.user_id = u.id
        WHERE 1=1
    """
    params = [current_user["user_id"]]
    
    # Filter visibility: show public snippets OR user's own private snippets
    if my_snippets:
        sql += " AND s.user_id = ?"
        params.append(current_user["user_id"])
    else:
        sql += " AND (s.is_private = 0 OR s.user_id = ?)"
        params.append(current_user["user_id"])
        
    if language:
        sql += " AND LOWER(s.language) = LOWER(?)"
        params.append(language)
        
    if tag:
        sql += " AND LOWER(s.tags) LIKE LOWER(?)"
        params.append(f"%{tag}%")
        
    if query:
        sql += " AND (LOWER(s.title) LIKE LOWER(?) OR LOWER(s.description) LIKE LOWER(?) OR LOWER(s.code_content) LIKE LOWER(?) OR LOWER(s.tags) LIKE LOWER(?))"
        q_wild = f"%{query}%"
        params.extend([q_wild, q_wild, q_wild, q_wild])
        
    sql += " ORDER BY s.created_at DESC"
    
    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    # Convert is_bookmarked integer to boolean
    for r in rows:
        r["is_bookmarked"] = bool(r["is_bookmarked"])
        r["is_private"] = bool(r["is_private"])
        
    return rows

@router.post("", status_code=status.HTTP_201_CREATED)
def create_snippet(
    snippet_data: SnippetCreate,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO snippets (user_id, title, description, code_content, language, tags, is_private, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user["user_id"],
        snippet_data.title,
        snippet_data.description or "",
        snippet_data.code_content,
        snippet_data.language.lower(),
        snippet_data.tags or "",
        1 if snippet_data.is_private else 0,
        now_iso,
        now_iso
    ))
    
    snippet_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "message": "Snippet created successfully",
        "snippet_id": snippet_id
    }

@router.get("/{snippet_id}")
def get_snippet(
    snippet_id: int,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Increment view count
    cursor.execute("UPDATE snippets SET views_count = views_count + 1 WHERE id = ?", (snippet_id,))
    conn.commit()
    
    cursor.execute("""
        SELECT s.*, u.full_name as author_name, u.username as author_username,
               (SELECT COUNT(*) FROM bookmarks b WHERE b.snippet_id = s.id AND b.user_id = ?) as is_bookmarked
        FROM snippets s
        JOIN users u ON s.user_id = u.id
        WHERE s.id = ?
    """, (current_user["user_id"], snippet_id))
    
    snippet = cursor.fetchone()
    conn.close()
    
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    res = dict(snippet)
    
    # Check authorization if snippet is private
    if res["is_private"] and res["user_id"] != current_user["user_id"] and current_user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Access denied to private snippet")
        
    res["is_bookmarked"] = bool(res["is_bookmarked"])
    res["is_private"] = bool(res["is_private"])
    return res

@router.put("/{snippet_id}")
def update_snippet(
    snippet_id: int,
    snippet_data: SnippetUpdate,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,))
    existing = cursor.fetchone()
    
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    if existing["user_id"] != current_user["user_id"] and current_user.get("role") != "Admin":
        conn.close()
        raise HTTPException(status_code=403, detail="You can only edit your own snippets")
        
    updates = snippet_data.dict(exclude_unset=True)
    if not updates:
        conn.close()
        return {"message": "No changes requested"}
        
    fields = []
    values = []
    
    for k, v in updates.items():
        if k == "is_private" and v is not None:
            fields.append("is_private = ?")
            values.append(1 if v else 0)
        elif k == "language" and v is not None:
            fields.append("language = ?")
            values.append(v.lower())
        elif v is not None:
            fields.append(f"{k} = ?")
            values.append(v)
            
    fields.append("updated_at = ?")
    values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    values.append(snippet_id)
    
    sql = f"UPDATE snippets SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    
    return {"message": "Snippet updated successfully"}

@router.delete("/{snippet_id}")
def delete_snippet(
    snippet_id: int,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM snippets WHERE id = ?", (snippet_id,))
    snippet = cursor.fetchone()
    
    if not snippet:
        conn.close()
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    if snippet["user_id"] != current_user["user_id"] and current_user.get("role") != "Admin":
        conn.close()
        raise HTTPException(status_code=403, detail="You can only delete your own snippets")
        
    cursor.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Snippet deleted successfully"}
