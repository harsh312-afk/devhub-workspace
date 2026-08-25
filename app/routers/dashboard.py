from fastapi import APIRouter, Depends
from app.database import get_db_connection
from app.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total public snippets or user's snippets
    cursor.execute("SELECT COUNT(*) as total FROM snippets WHERE is_private = 0 OR user_id = ?", (user_id,))
    total_accessible = cursor.fetchone()["total"]
    
    # User's own snippets
    cursor.execute("SELECT COUNT(*) as total FROM snippets WHERE user_id = ?", (user_id,))
    my_snippets_count = cursor.fetchone()["total"]
    
    # User's bookmarks
    cursor.execute("SELECT COUNT(*) as total FROM bookmarks WHERE user_id = ?", (user_id,))
    my_bookmarks_count = cursor.fetchone()["total"]
    
    # Total views on user's snippets
    cursor.execute("SELECT SUM(views_count) as total_views FROM snippets WHERE user_id = ?", (user_id,))
    res_views = cursor.fetchone()["total_views"]
    total_views = res_views if res_views else 0
    
    # Language breakdown
    cursor.execute("""
        SELECT language, COUNT(*) as count 
        FROM snippets 
        WHERE is_private = 0 OR user_id = ? 
        GROUP BY language 
        ORDER BY count DESC
    """, (user_id,))
    language_counts = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total_accessible_snippets": total_accessible,
        "my_snippets_count": my_snippets_count,
        "my_bookmarks_count": my_bookmarks_count,
        "total_snippet_views": total_views,
        "language_breakdown": language_counts
    }
