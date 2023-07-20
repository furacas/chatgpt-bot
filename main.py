import threading

from fastapi import FastAPI
from starlette.background import BackgroundTasks

from bot import models
from bot.db import engine
from chat.pandora_adapter import PandoraAdapter
from dingtalk.DingTalkAdapter import dingtalk_adapter
from dingtalk.schemas import DingtalkAskMessage
from wechat.WeChatAdapter import wechat_adapter
from wechat.wesdk import logging, Bot
from dingtalk.schemas import DingtalkAskMessage
from qq.QQAdapter import run_qq_bot
from wechat.WeChatAdapter import run_wechat_bot

app = FastAPI()

chatbot = PandoraAdapter()

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def index():
    return {"message": "Hello World"}


@app.post("/dingtalk/chat")
def chat(model: str = "gpt-3.5-turbo", message: DingtalkAskMessage = None, background_tasks: BackgroundTasks = None):
    print(f"model is {model}")
    background_tasks.add_task(lambda: dingtalk_adapter.process_message(message, model=model))
    return {"message": "Hello World"}


wechat_thread = threading.Thread(target=run_wechat_bot)
wechat_thread.start()

qq_thread = threading.Thread(target=run_qq_bot)
qq_thread.start()
