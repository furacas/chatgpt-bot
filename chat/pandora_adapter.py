import os
import uuid

import httpx

from .bot_adapter import ChatBotAdapter
from .schemas import AskResponse

PANDORA_SERVER_URL = os.environ.get('PANDORA_SERVER_URL') or "http://localhost:8080"


class PandoraAdapter(ChatBotAdapter):
    def ask(self, prompt, conversation_id, parent_id) -> AskResponse:
        data = {
            "prompt": prompt,
            "model": "gpt-3.5-turbo",
            "message_id": str(uuid.uuid4()),
            "parent_message_id": parent_id,
            "conversation_id": conversation_id,
            "stream": False
        }

        resp = httpx.post(PANDORA_SERVER_URL + '/api/conversation/talk', json=data, timeout=60).json()

        content = "".join(resp['message']['content']['parts'])
        conversation_id = resp['conversation_id']
        id = resp['message']['id']
        ask_result = AskResponse(content=content, conversation_id=conversation_id, id=id)
        return ask_result

    def change_title(self, conversation_id, title):
        pass

    def delete_conversation(self,conversation_id):
        httpx.delete(PANDORA_SERVER_URL + '/api/conversation/' + conversation_id, timeout=60)



chatbot = PandoraAdapter()
