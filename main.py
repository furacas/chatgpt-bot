import os
import uuid

from fastapi import FastAPI
from starlette.background import BackgroundTasks

from bot import models
from bot.db import SessionLocal, engine
from bot.models import Conversation
from chat.pandora_adapter import PandoraAdapter
from dingtalk.DingTalkAdapter import dingtalk_adapter
from dingtalk.schemas import DingtalkAskMessage, ChatType
from wechat.wesdk import logging, Bot

app = FastAPI()

chatbot = PandoraAdapter()

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def index():
    return {"message": "Hello World"}


@app.post("/dingtalk/chat")
def chat(message: DingtalkAskMessage, background_tasks: BackgroundTasks):
    background_tasks.add_task(lambda: dingtalk_adapter.process_message(message))
    return {"message": "Hello World"}


def send_msg(msg, bot):
    print(msg)

    prompt = msg['content'].strip()

    session = SessionLocal()
    row = session.query(Conversation).filter_by(chat_type=ChatType.wechat, target_id=msg['wxid']).first()

    conversation_id = row.gpt_conversation if row else ''
    parent_id = row.parent_conversation if row else str(uuid.uuid4())

    resp = chatbot.ask(prompt, conversation_id, parent_id)

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
        bot.register("recv_txt_msg", lambda msg: send_msg(msg, bot))
        bot.start()
    except:
        print("run we chat fail")

# run_webot()
