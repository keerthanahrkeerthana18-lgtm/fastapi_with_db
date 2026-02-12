from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from models import User
from schemas.chat_schemas import ChatCreate, ChatResponse, MessageCreate, MessageResponse
from repositories.chat_repo import ChatRepo
from utils.jwt_handler import verify_token
# We need a way to get current user. Let's reuse or create a dependency.
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.email == payload.get("email")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/chats", response_model=ChatResponse)
def create_new_chat(chat: ChatCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = ChatRepo(db)
    return repo.create_chat(current_user.id, chat)

@router.get("/chats", response_model=List[ChatResponse])
def get_chats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = ChatRepo(db)
    return repo.get_user_chats(current_user.id)

@router.get("/chats/{chat_id}", response_model=ChatResponse)
def get_chat_details(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = ChatRepo(db)
    chat = repo.get_chat(chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.post("/chats/{chat_id}/messages", response_model=MessageResponse)
def add_message(chat_id: int, message: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = ChatRepo(db)
    chat = repo.get_chat(chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return repo.add_message_to_chat(chat_id, message.content, message.role)

@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = ChatRepo(db)
    success = repo.delete_chat(chat_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"message": "Chat deleted successfully"}
