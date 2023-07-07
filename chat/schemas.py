from pydantic import BaseModel


class AskResponse(BaseModel):
    content: str
    conversation_id: str
    id: str
