import json

from bot.constants import HELP_MESSAGE
from bot.db import SessionLocal
from bot.message_handler import MessageHandler
from bot.models import Conversation
from chat.api_adapter import chatbot


class PlatformAdapter:

    def __init__(self, message_handler: MessageHandler):
        self.message_handler = message_handler

    def process_message(self, message, **kwargs):

        if not self.message_handler.should_handle_message(message):
            return

        prompt = self.message_handler.extract_prompt(message)

        if prompt.lower() in ("", "帮助", "help"):
            self.message_handler.send_response(HELP_MESSAGE, message, **kwargs)
            return

        chat_id, chat_type = self.message_handler.extract_id_and_type(message)

        session = SessionLocal()
        row = session.query(Conversation).filter_by(chat_type=chat_type, chat_id=chat_id).first()

        if prompt.lower() in ("重置", "reset"):
            if row:
                session.delete(row)
                session.commit()
                session.close()

            self.message_handler.send_response("重置成功", message, **kwargs)
            return

        if not row:
            context = []
        else:
            context = json.loads(row.context)

        context.append({
            "role": "user",
            "content": prompt
        })

        resp = chatbot.ask(context, **kwargs)

        context.append({
            "role": "assistant",
            "content": resp.content
        })

        if not row:
            row = Conversation(
                chat_type=chat_type,
                chat_id=chat_id,
                context=json.dumps(context)
            )
            session.add(row)
        else:
            row.context = json.dumps(context)

        self.message_handler.send_response(resp.content, message, **kwargs)
        session.commit()
        session.close()
