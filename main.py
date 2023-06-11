import uuid
from typing import Any, Dict

import httpx
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from bot import models
from bot.db import SessionLocal, engine
from bot.dintalk import DingTalk
from bot.models import Conversation
from bot.schemas import DingtalkAskMessage, ConversationTypeEnum
from chat.pandora_adapter import PandoraAdapter

app = FastAPI()

chatbot = PandoraAdapter()
ding_talk = DingTalk()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.commit()
        db.close()



@app.post("/dingtalk/chat")
def chat(message: DingtalkAskMessage, background_tasks: BackgroundTasks,session: Session = Depends(get_db)):
    prompt = message.text.content.strip()
    background_tasks.add_task(ask_and_reply,session, message)
    return {"message": "Hello World"}


async def ask_and_reply(
    session: Session,
    message: DingtalkAskMessage
):
    prompt = message.text.content.strip()

    if message.conversationType == ConversationTypeEnum.group:
        row = session.query(Conversation).filter_by(dingtalk_conversation=message.conversationId).first()
    else:
        row = session.query(Conversation).filter_by(dingtalk_user_id=message.senderStaffId).first()

    conversation_id = row.gpt_conversation if row else ''
    parent_id = row.parent_conversation if row else str(uuid.uuid4())

    resp = chatbot.ask(prompt,conversation_id,parent_id)

    if not row:
        if message.conversationType == ConversationTypeEnum.group:
            row = Conversation(
                dingtalk_conversation=message.conversationId,
                gpt_conversation=resp.conversation_id,
                parent_conversation=resp.id
            )
        else:
            row = Conversation(
                dingtalk_user_id=message.senderStaffId,
                gpt_conversation=resp.conversation_id,
                parent_conversation=resp.id
            )
        session.add(row)
    else:
        row.gpt_conversation = resp.conversation_id
        row.parent_conversation = resp.id

    content = resp.content
    title = content[:12]
    payload: Dict[str, Any] = {"msgtype": "text"}

    if message.conversationType == ConversationTypeEnum.group and message.senderStaffId:
        content = f"@{message.senderStaffId}\n\n{content}"
        payload["at"] = {"atUserIds": [message.senderStaffId]}

    payload["text"] = {"title": f" {title}", "content": content}

    httpx.post(message.sessionWebhook, json=payload)
