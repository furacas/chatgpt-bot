from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from .db import Base


class Conversation(Base):
    __tablename__ = "conversation_v2"
    id = Column(Integer, primary_key=True, index=True)
    gpt_conversation = Column(String)
    parent_conversation = Column(String)

    chat_type = Column(String, nullable=True)
    target_id = Column(String,nullable=True)
