from bot.message_handler import MessageHandler
from bot.platform_adapter import PlatformAdapter
from bot.sender import Sender


class WeChatMessageHandler(MessageHandler):

    def extract_id_and_type(self, message):
        pass

    def extract_prompt(self, message):
        pass


class WeChatSender(Sender):
    def send_response(self, content, message):
        pass


class WeChatAdapter(PlatformAdapter):
    def __int__(self, **kwargs):
        super().__int__(WeChatMessageHandler(), WeChatSender())


wechat_adapter = WeChatAdapter()
