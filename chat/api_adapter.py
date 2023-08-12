import openai

from .bot_adapter import ChatBotAdapter
from .schemas import AskResponse


class ApiAdapter(ChatBotAdapter):
    def ask(self, context, **kwargs) -> AskResponse:
        model = kwargs.get('model', 'gpt-3.5-turbo')
        response = openai.ChatCompletion.create(
            model=model,
            messages=context,
            stream=False
        )

        content = response['choices'][0]['message']['content']
        ask_result = AskResponse(content=content)
        return ask_result


chatbot = ApiAdapter()
