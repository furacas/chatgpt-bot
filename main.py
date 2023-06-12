import os
import uuid
from typing import Any, Dict

import httpx
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from bot import models
from bot.constants import HELP_MESSAGE
from bot.db import SessionLocal, engine
from bot.dintalk import DingTalk
from bot.models import Conversation
from bot.schemas import DingtalkAskMessage, ConversationTypeEnum, ChatType
from chat.pandora_adapter import PandoraAdapter
from wesdk import logging,  Bot

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

@app.get("/")
def index():
    return {"message": "Hello World"}

@app.post("/dingtalk/chat")
def chat(message: DingtalkAskMessage, background_tasks: BackgroundTasks,session: Session = Depends(get_db)):
    background_tasks.add_task(ask_and_reply,session, message)
    return {"message": "Hello World"}


async def ask_and_reply(
    session: Session,
    message: DingtalkAskMessage
):
    prompt = message.text.content.strip()
    if prompt.lower() in ("", "帮助", "help"):
        send_dingtalk(HELP_MESSAGE, message)
        return

    if message.conversationType == ConversationTypeEnum.group:
        row = session.query(Conversation).filter_by(chat_type=ChatType.dingtalk_group,target_id=message.conversationId).first()
    else:
        row = session.query(Conversation).filter_by(chat_type=ChatType.dingtalk,target_id=message.senderStaffId).first()

    conversation_id = row.gpt_conversation if row else ''
    parent_id = row.parent_conversation if row else str(uuid.uuid4())

    resp = chatbot.ask(prompt,conversation_id,parent_id)

    if not row:
        if message.conversationType == ConversationTypeEnum.group:
            row = Conversation(
                chat_type=ChatType.dingtalk_group,
                target_id=message.conversationId,
                gpt_conversation=resp.conversation_id,
                parent_conversation=resp.id
            )
        else:
            row = Conversation(
                chat_type=ChatType.dingtalk,
                target_id=message.senderStaffId,
                gpt_conversation=resp.conversation_id,
                parent_conversation=resp.id
            )
        session.add(row)
    else:
        row.gpt_conversation = resp.conversation_id
        row.parent_conversation = resp.id

    content = resp.content

    send_dingtalk(content,message)

def send_dingtalk(content,message: DingtalkAskMessage):
    title = content[:12]
    payload: Dict[str, Any] = {"msgtype": "text"}

    if message.conversationType == ConversationTypeEnum.group and message.senderStaffId:
        content = f"@{message.senderStaffId}\n\n{content}"
        payload["at"] = {"atUserIds": [message.senderStaffId]}

    payload["text"] = {"title": f" {title}", "content": content}

    httpx.post(message.sessionWebhook, json=payload)
def send_msg(msg,bot):
    print(msg)

    prompt = msg['content'].strip()

    session = SessionLocal()
    row = session.query(Conversation).filter_by(chat_type=ChatType.wechat, target_id=msg['wxid']).first()

    conversation_id = row.gpt_conversation if row else ''
    parent_id = row.parent_conversation if row else str(uuid.uuid4())

    resp = chatbot.ask(prompt,conversation_id,parent_id)

    if not row:
        row = Conversation(
            chat_type=ChatType.wechat,
            target_id=msg['wxid'],
            gpt_conversation=resp.conversation_id,
            parent_conversation=resp.id
        )
        session.add(row)
    else:
        row.gpt_conversation = resp.conversation_id
        row.parent_conversation = resp.id

    bot.send_msg(resp.content, msg['wxid'])

    session.commit()
    session.close()
    return None

def run_webot():
    try:
        WE_SERVICE = os.environ.get('WE_SERVICE') or "localhost"
        bot = Bot(ip=WE_SERVICE)
        bot.register("on_open", lambda ws: logging("Connecting to WeChat service .."))
        bot.register("on_close", lambda ws: logging("Byebye~"))
        bot.register("recv_txt_msg",lambda msg: send_msg(msg,bot))
        bot.start()
    except:
        print("run we chat fail")

run_webot()
