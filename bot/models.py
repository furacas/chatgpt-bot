from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from .db import Base


class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(Integer, primary_key=True, index=True)
    gpt_conversation = Column(String)
    parent_conversation = Column(String)
    dingtalk_conversation = Column(String,nullable=True)
    dingtalk_user_id = Column(String,nullable=True)
