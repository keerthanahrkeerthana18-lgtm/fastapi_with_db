from sqlalchemy.orm import Session
from models import Chat, Message
from schemas.chat_schemas import ChatCreate

class ChatRepo:
    def __init__(self, db: Session):
        self.db = db

    def create_chat(self, user_id: int, chat_data: ChatCreate):
        db_chat = Chat(user_id=user_id, title=chat_data.title)
        self.db.add(db_chat)
        self.db.commit()
        self.db.refresh(db_chat)
        return db_chat

    def get_user_chats(self, user_id: int):
        return self.db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at.desc()).all()

    def get_chat(self, chat_id: int, user_id: int):
        chat = self.db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
        return chat

    def add_message_to_chat(self, chat_id: int, content: str, role: str):
        db_message = Message(chat_id=chat_id, role=role, content=content)
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def delete_chat(self, chat_id: int, user_id: int):
        chat = self.get_chat(chat_id, user_id)
        if chat:
            self.db.delete(chat)
            self.db.commit()
            return True
        return False
