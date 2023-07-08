import os
import time

import httpx

from bot.message_handler import MessageHandler
from bot.platform_adapter import PlatformAdapter
from dingtalk.schemas import ChatType


class QQMessageHandler(MessageHandler):
    def extract_id_and_type(self, message):
        if message['type'] == 'FriendMessage':
            return message['sender']['id'], ChatType.qq
        else:
            return message['sender']['group']['id'], ChatType.qq

    def extract_prompt(self, message):
        return self.get_plain_text(message)

    def send_response(self, content, message, **kwargs):
        payload = {
            "sessionKey": kwargs["session_key"],
            "messageChain": [
                {"type": "Plain", "text": content}
            ],
            "quote": self.get_message_id(message)
        }

        if message['type'] == 'GroupMessage':
            payload['target'] = message['sender']['group']['id']
            httpx.post(kwargs['qq_service'] + f"/sendGroupMessage", json=payload)
        else:
            payload['target'] = message['sender']['id']
            httpx.post(kwargs['qq_service'] + f"/sendFriendMessage", json=payload)

    def get_plain_text(self, message):
        message_list = list(filter(lambda obj: obj['type'] == 'Plain', message['messageChain']))
        if message_list:
            return "".join([obj['text'] for obj in message_list])
        return None

    def get_message_id(self, message):
        return message['messageChain'][0]['id']

    def should_handle_message(self, message):
        if not self.get_plain_text(message):
            return False

        if message['type'] == 'GroupMessage':
            at_list = list(filter(lambda obj: obj['type'] == 'At' and str(obj['target']) == os.environ.get('QQ_NUM'),
                                  message['messageChain']))
            return len(at_list) > 0

        return True


class QQAdapter(PlatformAdapter):
    def __init__(self):
        super().__init__(QQMessageHandler())


qq_adapter = QQAdapter()


def bind_session():
    QQ_SERVICE = os.environ.get('QQ_SERVICE')
    QQ_NUM = os.environ.get('QQ_NUM')

    resp = httpx.post(QQ_SERVICE + "/verify", json={'verifyKey': ''})

    resp_data = resp.json()
    payload = {
        "qq": QQ_NUM,
        "sessionKey": resp_data['session'],
    }
    httpx.post(QQ_SERVICE + "/bind", json=payload)

    return resp_data['session']


def run_qq_bot():
    QQ_SERVICE = os.environ.get('QQ_SERVICE')

    if not QQ_SERVICE:
        print("qq bot not start since QQ_SERVICE is not set")
        return

    print("start qq bot")

    session_key = bind_session()

    while True:
        try:
            datas = httpx.get(QQ_SERVICE + f"/fetchMessage?sessionKey={session_key}&count=1").json()['data']

            if datas:
                for data in datas:
                    qq_adapter.process_message(data, session_key=session_key, qq_service=QQ_SERVICE)
        except:
            pass

        time.sleep(5)
