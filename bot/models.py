from sqlalchemy import Column, Integer, String

from .db import Base


class Conversation(Base):
    __tablename__ = "conversation_v3"
    id = Column(Integer, primary_key=True, index=True)
    gpt_conversation = Column(String)
    parent_conversation = Column(String)

    chat_type = Column(String, nullable=True)
    chat_id = Column(String, nullable=True)
