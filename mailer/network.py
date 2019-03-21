from collections import ChainMap
from email.message import EmailMessage
from fnmatch import fnmatch
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .daemon import Daemon
    from .message import UserEmail


class Network:
    def __init__(self, name, server_pattern, config, core: 'Daemon'):
        self.core = core
        self.name = name
        self.server_pattern = server_pattern
        self.config = config
        self.smtp_config = config['smtp']
        self.formats = {}

    @classmethod
    def from_config(cls, core: 'Daemon', net_config, config):
        net_obj = cls(net_config['name'], net_config['server'], net_config, core)
        net_obj.formats.update(config.default_formats)
        net_obj.formats.update(net_config.get('formats', {}))
        return net_obj

    def match_server(self, server):
        return fnmatch(server, self.server_pattern)

    def format_message(self, message: 'UserEmail'):
        fmt = self.formats[message.message_type]
        data = ChainMap({'network': self.name}, message.data)
        return fmt['subject'].format_map(data), fmt['message'].format_map(data)

    def send_email(self, message: 'UserEmail'):
        subject, body = self.format_message(message)
        email = EmailMessage()
        email.set_payload(body)
        email['Subject'] = subject
        email['To'] = message.user_email

        self.core.send_message(self.smtp_config, email)
