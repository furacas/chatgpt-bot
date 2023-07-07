import os

from bot.message_handler import MessageHandler
from bot.platform_adapter import PlatformAdapter
from dingtalk.schemas import ChatType


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
