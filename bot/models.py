from sqlalchemy import Column, Integer, String

from .db import Base


class Conversation(Base):
    __tablename__ = "conversation_v5"
    id = Column(Integer, primary_key=True, index=True)
    context = Column(String)

    chat_type = Column(String, nullable=True)
    chat_id = Column(String, nullable=True)
