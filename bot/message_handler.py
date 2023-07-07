

class MessageHandler:
    def extract_id_and_type(self, message):
        return message.id, message.type

    def extract_prompt(self, message):
        pass

    def send_response(self, content, message,kwargs):
        pass

    def should_handle_message(self,message):
        return True

