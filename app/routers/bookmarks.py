from fastapi import APIRouter, HTTPException, Depends, status
from app.database import get_db_connection
from app.auth import get_current_user
from app.schemas import BookmarkToggleResponse

router = APIRouter(prefix="/api/bookmarks", tags=["Bookmarks"])

@router.post("/{snippet_id}/toggle", response_model=BookmarkToggleResponse)
def toggle_bookmark(
    snippet_id: int,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if snippet exists
    cursor.execute("SELECT id FROM snippets WHERE id = ?", (snippet_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    user_id = current_user["user_id"]
    cursor.execute("SELECT id FROM bookmarks WHERE user_id = ? AND snippet_id = ?", (user_id, snippet_id))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("DELETE FROM bookmarks WHERE id = ?", (existing["id"],))
        conn.commit()
        conn.close()
        return BookmarkToggleResponse(
            message="Removed from bookmarks",
            is_bookmarked=False,
            snippet_id=snippet_id
        )
    else:
        cursor.execute("INSERT INTO bookmarks (user_id, snippet_id) VALUES (?, ?)", (user_id, snippet_id))
        conn.commit()
        conn.close()
        return BookmarkToggleResponse(
            message="Added to bookmarks",
            is_bookmarked=True,
            snippet_id=snippet_id
        )

@router.get("")
def get_user_bookmarks(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.*, u.full_name as author_name, u.username as author_username, 1 as is_bookmarked
        FROM bookmarks b
        JOIN snippets s ON b.snippet_id = s.id
        JOIN users u ON s.user_id = u.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    """, (current_user["user_id"],))
    
    bookmarks = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    for r in bookmarks:
        r["is_bookmarked"] = True
        r["is_private"] = bool(r["is_private"])
        
    return bookmarks
