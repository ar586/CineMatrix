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

@router.get("", response_model=List[Comment])
def get_comments(movie_id: str, db: Annotated[any, Depends(get_db)]):
    if db is None:
        raise HTTPException(500, "DB Connection Failed")
        
    cursor = db.comments.find({"movie_id": movie_id}).sort("created_at", -1)
    return list(cursor)

@router.post("", response_model=Comment)
def add_comment(
    movie_id: str,
    db: Annotated[any, Depends(get_db)],
    comment_data: dict = Body(...),
    current_user: UserInDB = Depends(get_current_user)
):
    if db is None:
        raise HTTPException(500, "DB Connection Failed")
    
    from bson import ObjectId
    
    # Handle parent_id conversion
    parent_id = comment_data.get("parent_id")
    if parent_id:
        try:
            parent_id = ObjectId(parent_id)
        except:
            raise HTTPException(400, "Invalid parent_id")
    
    # Create comment document
    new_comment = Comment(
        movie_id=movie_id,
        user_id=current_user.username,
        username=current_user.username,
        text=comment_data.get("text"),
        rating=comment_data.get("rating"),
        parent_id=str(parent_id) if parent_id else None,
        created_at=datetime.utcnow()
    )
    
    comment_dict = new_comment.model_dump(by_alias=True, exclude=["id"])
    result = db.comments.insert_one(comment_dict)
    
    # If this is a reply, update parent's replies array
    if parent_id:
        db.comments.update_one(
            {"_id": parent_id},
            {"$push": {"replies": str(result.inserted_id)}}
        )
    
    return db.comments.find_one({"_id": result.inserted_id})

@router.post("/{comment_id}/like")
def like_comment(
    movie_id: str,
    comment_id: str,
    db: Annotated[any, Depends(get_db)],
    current_user: UserInDB = Depends(get_current_user)
):
    if db is None:
        raise HTTPException(500, "DB Connection Failed")
    
    from bson import ObjectId
    comment = db.comments.find_one({"_id": ObjectId(comment_id), "movie_id": movie_id})
    if not comment:
        raise HTTPException(404, "Comment not found")
    
    username = current_user.username
    liked_by = comment.get("liked_by", [])
    disliked_by = comment.get("disliked_by", [])
    
    # Toggle like
    if username in liked_by:
        # Unlike
        db.comments.update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$pull": {"liked_by": username},
                "$inc": {"likes": -1}
            }
        )
    else:
        # Like (and remove dislike if exists)
        update_ops = {
            "$addToSet": {"liked_by": username},
            "$inc": {"likes": 1}
        }
        if username in disliked_by:
            update_ops["$pull"] = {"disliked_by": username}
            update_ops["$inc"]["dislikes"] = -1
        
        db.comments.update_one({"_id": ObjectId(comment_id)}, update_ops)
    
    return db.comments.find_one({"_id": ObjectId(comment_id)})

@router.post("/{comment_id}/dislike")
def dislike_comment(
    movie_id: str,
    comment_id: str,
    db: Annotated[any, Depends(get_db)],
    current_user: UserInDB = Depends(get_current_user)
):
    if db is None:
        raise HTTPException(500, "DB Connection Failed")
    
    from bson import ObjectId
    comment = db.comments.find_one({"_id": ObjectId(comment_id), "movie_id": movie_id})
    if not comment:
        raise HTTPException(404, "Comment not found")
    
    username = current_user.username
    liked_by = comment.get("liked_by", [])
    disliked_by = comment.get("disliked_by", [])
    
    # Toggle dislike
    if username in disliked_by:
        # Remove dislike
        db.comments.update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$pull": {"disliked_by": username},
                "$inc": {"dislikes": -1}
            }
        )
    else:
        # Dislike (and remove like if exists)
        update_ops = {
            "$addToSet": {"disliked_by": username},
            "$inc": {"dislikes": 1}
        }
        if username in liked_by:
            update_ops["$pull"] = {"liked_by": username}
            update_ops["$inc"]["likes"] = -1
        
        db.comments.update_one({"_id": ObjectId(comment_id)}, update_ops)
    
    return db.comments.find_one({"_id": ObjectId(comment_id)})

@router.get("/{comment_id}/replies", response_model=List[Comment])
def get_replies(
    movie_id: str,
    comment_id: str,
    db: Annotated[any, Depends(get_db)]
):
    if db is None:
        raise HTTPException(500, "DB Connection Failed")
    
    # Get all comments where parent_id matches this comment_id
    cursor = db.comments.find({
        "movie_id": movie_id,
        "parent_id": comment_id
    }).sort("created_at", 1)  # Oldest first for replies
    
    return list(cursor)
