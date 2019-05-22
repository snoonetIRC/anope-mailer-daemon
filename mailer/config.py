from collections import ChainMap
from email.message import Message
from pathlib import Path
from smtplib import SMTP
from typing import Dict

import yaml

from mailer.email_template import EmailTemplate
from .network import Network
from .reporter import ErrorReporter

__all__ = ('SMTPConfig', 'Config')


class SMTPConfig:
    def __init__(self, name, server, port=None, tls=False, user_name=None, password=None, smtp_helo=None, from_addr=None):
        self.name = name
        self.server = server
        self.port = port
        self.tls = tls
        self.user_name = user_name
        self.password = password
        self.smtp_helo = smtp_helo
        self.from_addr = from_addr

    @classmethod
    def from_config(cls, name, config):
        return cls(name, **config)

    def send(self, message: 'Message'):
        if self.from_addr:
            try:
                message.replace_header('From', self.from_addr)
            except KeyError:
                message['From'] = self.from_addr

        with SMTP(self.server, self.port) as smtp:
            if self.tls:
                smtp.starttls()

            if self.smtp_helo:
                smtp.helo(self.smtp_helo)

            if self.user_name and self.password:
                smtp.login(self.user_name, self.password)

            print("Sending email to {!r} using config {!r}".format(
                message['To'], self.name
            ))
            smtp.send_message(message)


class Config:
    @staticmethod
    def compile_templates(config) -> Dict[str, EmailTemplate]:
        return {
            name: EmailTemplate.from_config(data)
            for name, data in config.items()
        }

    def __init__(self, filename, core):
        self.core = core
        with Path(filename).resolve().open() as f:
            data = yaml.safe_load(f)

        self.config = data
        self.default_formats = self.compile_templates(
            data.get('default_formats', {})
        )
        self.api_url = data['api']
        self.mail_dir = Path(data.get('mail_dir', 'emails')).resolve()
        self.smtp_configs = {
            name: SMTPConfig.from_config(name, data)
            for name, data in data['smtp'].items()
        }

        self.networks = [
            Network.from_config(self.core, net, self)
            for net in data.get('networks', [])
        ]

        self.reports_config = data.get('reports')
        self.reporters_defaults = self.reports_config.pop('default', {})

        self.error_reporter = ErrorReporter(
            self.get_reporter_config('errors'),
            self.core
        )

    def get_reporter_config(self, name):
        return ChainMap(
            self.reports_config.get(name, {}),
            self.reporters_defaults
        )
