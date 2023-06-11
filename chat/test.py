import uuid

import httpx

data = {
    "prompt": "你好",
    "model": "gpt-3.5-turbo",
    "message_id": str(uuid.uuid4()),
    "parent_message_id": str(uuid.uuid4()),
    "conversation_id": '',
    "stream": False
}

print(data)

resp = httpx.post('http://localhost:8080/api/conversation/talk', json=data)

print(resp.json())