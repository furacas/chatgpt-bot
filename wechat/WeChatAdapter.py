import os
import time

from bot.message_handler import MessageHandler
from bot.platform_adapter import PlatformAdapter
from dingtalk.schemas import ChatType
from wechat.wesdk import Bot, logging


class WeChatMessageHandler(MessageHandler):

    def extract_id_and_type(self, message):
        return ChatType.wechat, message['wxid']

    def extract_prompt(self, message):
        return message['content'].strip()

    def send_response(self, content, message, **kwargs):
        bot = kwargs['bot']
        if self.is_group(message):
            # 群聊
            bot.send_msg(content, message['wxid'], message['roomid'], message['nickname'])
        else:
            bot.send_msg(content, message['wxid'])

    def should_handle_message(self, message):
        if self.is_group(message):
            if message.get('at_nickname', None) == os.environ.get('WE_BOT_NAME', '普罗米修斯'):
                return True
            return False
        return True

    def is_group(self, message):
        return message['roomid'] and message['wxid']


class WeChatAdapter(PlatformAdapter):
    def __init__(self):
        super().__init__(WeChatMessageHandler())


wechat_adapter = WeChatAdapter()


def run_wechat_bot():
    bot = None

    WE_SERVICE = os.environ.get('WE_SERVICE')

    if not WE_SERVICE:
        return

    while True:
        if not bot or not bot.is_alive():
            print('start wechat bot')
            try:
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
