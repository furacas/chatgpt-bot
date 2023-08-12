from typing import Any, Dict

import httpx

from bot.message_handler import MessageHandler
from bot.platform_adapter import PlatformAdapter
from dingtalk.schemas import DingtalkAskMessage, ConversationTypeEnum, ChatType


class DingTalkMessageHandler(MessageHandler):
    def extract_id_and_type(self, message: DingtalkAskMessage):
        if message.conversationType == ConversationTypeEnum.group:
            return message.conversationId, ChatType.dingtalk_group
        else:
            return message.senderStaffId, ChatType.dingtalk

    def extract_prompt(self, message: DingtalkAskMessage):
        return message.text.content.strip()

    def send_response(self, content, message,**kwargs):
        title = content[:12]
        payload: Dict[str, Any] = {"msgtype": "text"}
        if message.conversationType == ConversationTypeEnum.group and message.senderStaffId:
            content = f"@{message.senderStaffId}\n\n{content}"
            payload["at"] = {"atUserIds": [message.senderStaffId]}

        payload["text"] = {"title": f" {title}", "content": content}

        resp = httpx.post(message.sessionWebhook, json=payload)
        print(resp.content)


class DingTalkAdapter(PlatformAdapter):
    def __init__(self):
        super().__init__(DingTalkMessageHandler())


dingtalk_adapter = DingTalkAdapter()
