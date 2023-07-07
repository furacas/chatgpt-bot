from abc import ABC, abstractmethod

from chat.schemas import AskResponse


class ChatBotAdapter(ABC):

    @abstractmethod
    def ask(self,prompt,conversation_id,parent_id) -> AskResponse:
        pass

    @abstractmethod
    def change_title(self,conversation_id,title):
        pass