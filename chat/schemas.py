from pydantic import BaseModel


class AskResponse(BaseModel):
    content: str
