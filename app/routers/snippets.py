from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import PlainTextResponse
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
    
    # Convert is_bookmarked and is_private to boolean
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
        snippet_data.title.strip(),
        (snippet_data.description or "").strip(),
        snippet_data.code_content,
        snippet_data.language.strip().lower(),
        (snippet_data.tags or "").strip(),
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
    
    cursor.execute("""
        SELECT s.*, u.full_name as author_name, u.username as author_username,
               (SELECT COUNT(*) FROM bookmarks b WHERE b.snippet_id = s.id AND b.user_id = ?) as is_bookmarked
        FROM snippets s
        JOIN users u ON s.user_id = u.id
        WHERE s.id = ?
    """, (current_user["user_id"], snippet_id))
    
    snippet = cursor.fetchone()
    
    if not snippet:
        conn.close()
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    res = dict(snippet)
    
    # Check authorization if snippet is private
    if res["is_private"] and res["user_id"] != current_user["user_id"] and current_user.get("role") != "Admin":
        conn.close()
        raise HTTPException(status_code=403, detail="Access denied to private snippet")
        
    # Increment view count only after authorized retrieval
    cursor.execute("UPDATE snippets SET views_count = views_count + 1 WHERE id = ?", (snippet_id,))
    conn.commit()
    conn.close()
    
    res["views_count"] = res["views_count"] + 1
    res["is_bookmarked"] = bool(res["is_bookmarked"])
    res["is_private"] = bool(res["is_private"])
    return res

@router.get("/{snippet_id}/raw", response_class=PlainTextResponse)
def get_raw_snippet(
    snippet_id: int,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,))
    snippet = cursor.fetchone()
    conn.close()
    
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    if snippet["is_private"] and snippet["user_id"] != current_user["user_id"] and current_user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Access denied to private snippet")
        
    return PlainTextResponse(content=snippet["code_content"], media_type="text/plain; charset=utf-8")

@router.post("/{snippet_id}/fork", status_code=status.HTTP_201_CREATED)
def fork_snippet(
    snippet_id: int,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,))
    original = cursor.fetchone()
    
    if not original:
        conn.close()
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    if original["is_private"] and original["user_id"] != current_user["user_id"] and current_user.get("role") != "Admin":
        conn.close()
        raise HTTPException(status_code=403, detail="Cannot fork a private snippet")
        
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fork_title = f"{original['title']} (Forked)"
    fork_desc = f"Forked from #{original['id']}. {original['description'] or ''}".strip()
    
    cursor.execute("""
        INSERT INTO snippets (user_id, title, description, code_content, language, tags, is_private, views_count, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?, ?)
    """, (
        current_user["user_id"],
        fork_title,
        fork_desc,
        original["code_content"],
        original["language"],
        original["tags"],
        now_iso,
        now_iso
    ))
    
    new_snippet_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "message": "Snippet successfully forked to your workspace",
        "snippet_id": new_snippet_id
    }

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
        
    if hasattr(snippet_data, "model_dump"):
        updates = snippet_data.model_dump(exclude_unset=True)
    else:
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
            values.append(v.strip().lower())
        elif v is not None:
            fields.append(f"{k} = ?")
            values.append(v.strip() if isinstance(v, str) else v)
            
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
