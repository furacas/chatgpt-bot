import os
import threading
import time

from fastapi import FastAPI
from starlette.background import BackgroundTasks

from bot import models
from bot.db import engine
from chat.pandora_adapter import PandoraAdapter
from dingtalk.DingTalkAdapter import dingtalk_adapter
from dingtalk.schemas import DingtalkAskMessage, ChatType
from wechat.WeChatAdapter import wechat_adapter
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


def run_wechat_bot():
    bot = None

    while True:
        if not bot or not bot.is_alive():
            print('start wechat bot')
            try:
                WE_SERVICE = os.environ.get('WE_SERVICE') or "localhost"
                bot = Bot(ip=WE_SERVICE)
                bot.register("on_open", lambda ws: logging("Connecting to WeChat service .."))
                bot.register("on_close", lambda ws: logging("Byebye~"))
                bot.register("recv_txt_msg", lambda msg: wechat_adapter.process_message(msg, bot=bot))
                bot.start()
            except:
                print("start wechat bot fail will retry in 5 s")
                pass
            print('end start wechat bot')
        time.sleep(5)


wechat_thread = threading.Thread(target=run_wechat_bot)
wechat_thread.start()
