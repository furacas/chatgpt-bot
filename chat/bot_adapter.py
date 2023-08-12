from abc import ABC, abstractmethod

from chat.schemas import AskResponse


class ChatBotAdapter(ABC):

    @abstractmethod
    def ask(self, prompt, conversation_id, parent_id, **kwargs) -> AskResponse:
        pass
