from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from backend import config
from backend.auth.utils import (
    Token,
    User,
    UserInDB,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password
)
from backend.database.deps import get_db

router = APIRouter(prefix="/api/auth", tags=["authentication"])

class UserCreate(BaseModel):
    username: str
    password: str
    email: str | None = None
    full_name: str | None = None

@router.post("/register", response_model=User)
async def register(user: UserCreate, db: Annotated[any, Depends(get_db)]):
    
    # Check if user exists
    existing_user = db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    user_doc = {
        "username": user.username,
        "hashed_password": hashed_password,
        "email": user.email,
        "full_name": user.full_name,
        "disabled": False
    }
    
    db.users.insert_one(user_doc)
    return User(**user_doc)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[any, Depends(get_db)]
):
    
    user_doc = db.users.find_one({"username": form_data.username})
    user = None
    if user_doc:
        user = UserInDB(**user_doc)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
