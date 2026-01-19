from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List
from datetime import datetime
from backend.database.models import Comment
from backend.auth.utils import get_current_user, UserInDB
from backend.database.deps import get_db
import logging
from typing import Annotated

logger = logging.getLogger("API.Discussion")

router = APIRouter(prefix="/api/movies/{movie_id}/comments", tags=["discussion"])

@router.get("/", response_model=List[Comment])
def get_comments(movie_id: str, db: Annotated[any, Depends(get_db)]):
    if db is None:
        raise HTTPException(500, "DB Connection Failed")
        
    cursor = db.comments.find({"movie_id": movie_id}).sort("created_at", -1)
    return list(cursor)

@router.post("/", response_model=Comment)
def add_comment(
    movie_id: str,
    db: Annotated[any, Depends(get_db)],
    comment_data: dict = Body(...),
    current_user: UserInDB = Depends(get_current_user)
):
    if db is None:
        raise HTTPException(500, "DB Connection Failed")
    
    # Create comment document
    new_comment = Comment(
        movie_id=movie_id,
        user_id=current_user.username, # Using username as ID for simplicity or could use _id if we had it easily accessible as string
        username=current_user.username,
        text=comment_data.get("text"),
        rating=comment_data.get("rating"),
        created_at=datetime.utcnow()
    )
    
    # Validate manually if needed or trust Pydantic (Pydantic will validate on return but we need to insert dict)
    comment_dict = new_comment.model_dump(by_alias=True, exclude=["id"])
    
    result = db.comments.insert_one(comment_dict)
    
    # Return created comment
    return db.comments.find_one({"_id": result.inserted_id})
