from bot.message_handler import MessageHandler
from bot.platform_adapter import PlatformAdapter
from bot.sender import Sender
from dingtalk.schemas import ChatType


class WeChatMessageHandler(MessageHandler):

    def extract_id_and_type(self, message):

        return ChatType.wechat, message['wxid']

    def extract_prompt(self, message):
        return message['content'].strip()


class WeChatSender(Sender):
    def send_response(self, content, message,**kwargs):
        bot = kwargs['bot']
        bot.send_msg(content, message['wxid'])


class WeChatAdapter(PlatformAdapter):
    def __init__(self):
        super().__init__(WeChatMessageHandler(), WeChatSender())


wechat_adapter = WeChatAdapter()
