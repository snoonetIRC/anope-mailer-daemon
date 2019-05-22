from collections import ChainMap
from email import message_from_string, policy
from email.message import EmailMessage
from fnmatch import fnmatch
from typing import Dict, TYPE_CHECKING

from mailer.email_template import EmailTemplate

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
        self.formats: Dict[str, EmailTemplate] = {}

    @classmethod
    def from_config(cls, core: 'Daemon', net_config, config):
        net_obj = cls(net_config['name'], net_config['server'], net_config, core)
        net_obj.formats.update(config.default_formats)
        net_obj.formats.update(config.compile_templates(
            net_config.get('formats', {})
        ))
        return net_obj

    def match_server(self, server):
        return fnmatch(server, self.server_pattern)

    def format_message(self, message: 'UserEmail'):
        fmt = self.formats[message.message_type]
        data = ChainMap({'network': self.name}, message.data)
        return fmt.generate(data)

    def send_email(self, message: 'UserEmail'):
        email: EmailMessage = message_from_string(
            self.format_message(message),
            policy=policy.SMTP,
        )
        del email['To']
        email['To'] = message.user_email

        self.core.send_message(self.smtp_config, email)
