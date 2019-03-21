from email import message_from_file
from email.message import Message
from pathlib import Path


class UserEmail:
    def __init__(self, headers, data):
        self.headers = headers
        self.data = data
        self.user = data['nick']
        self.message_type = data['type']
        self.user_email = headers['To']

    @classmethod
    def from_file(cls, file: Path):
        with file.open(encoding='utf8') as f:
            message = message_from_file(f)  # type: Message

        return cls.from_message(message)

    @classmethod
    def from_message(cls, message: Message):
        headers = dict(message.items())
        data = {}
        if message.is_multipart():
            parts = [part.get_payload() for part in message.get_payload()]
        else:
            parts = message.get_payload().splitlines()

        for line in parts:
            key, _, value = line.partition('=')
            if key:
                data[key] = value

        return cls(headers, data)
