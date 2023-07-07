import uuid

from bot.constants import HELP_MESSAGE
from bot.db import SessionLocal
from bot.message_handler import MessageHandler
from bot.models import Conversation
from chat.pandora_adapter import chatbot


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

        conversation_id = row.gpt_conversation if row else ''
        parent_id = row.parent_conversation if row else str(uuid.uuid4())

        if prompt.lower() in ("重置","reset"):
            if row:
                session.delete(row)
                session.commit()
                session.close()
            if conversation_id:
                chatbot.delete_conversation(conversation_id)

            self.message_handler.send_response("重置成功", message, **kwargs)
            return

        resp = chatbot.ask(prompt, conversation_id, parent_id)

        if not row:
            row = Conversation(
                chat_type=chat_type,
                chat_id=chat_id,
                gpt_conversation=resp.conversation_id,
                parent_conversation=resp.id
            )
            session.add(row)
        else:
            row.gpt_conversation = resp.conversation_id
            row.parent_conversation = resp.id

        self.message_handler.send_response(resp.content, message, **kwargs)
        session.commit()
        session.close()
