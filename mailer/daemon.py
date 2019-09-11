import os
import random
import smtplib
import time
import traceback
from typing import Union

import requests

from .config import SMTPConfig, Config
from .message import UserEmail


class Daemon:
    def __init__(self):
        self.config = Config(os.getenv('MAILER_CONFIG', 'config.yaml'), self)

    def send_message(self, smtp_config: Union[str, SMTPConfig], message):
        if isinstance(smtp_config, str):
            smtp_config = self.config.smtp_configs[smtp_config]

        try:
            smtp_config.send(message)
        except smtplib.SMTPRecipientsRefused as e:
            self.error_reporter.report_warning(
                "Invalid email recipient(s) {!r}, ignoring message".format(e.recipients)
            )

    def on_error(self):
        """Must only be called while handling an exception"""
        traceback.print_exc()
        if self.error_reporter:
            self.error_reporter.report_error(traceback.format_exc())

    def get_email_files(self):
        files = list(self.mail_dir.rglob('*.mail'))
        random.shuffle(files)
        return files

    def get_network(self, nick):
        server = self.get_reg_server(nick)
        if server is None:
            return None

        for net in self.config.networks:
            if net.match_server(server):
                return net

        return None

    def get_reg_server(self, nick):
        with requests.get(
                self.config.api_url + '/api/user',
                params={'name': nick}
        ) as response:
            data = response.json()

        try:
            return data['nc']['REGSERVER']
        except KeyError:
            # If the nick was registered more than an hour ago,
            # assume it should use the default network
            if data['time_registered'] < (time.time() - 3600):
                return 'default'

            return None

    @property
    def mail_dir(self):
        return self.config.mail_dir

    @property
    def error_reporter(self):
        return self.config.error_reporter

    def tick(self):
        self.error_reporter.tick()

    def handle_email(self, file):
        email = UserEmail.from_file(file)
        net = self.get_network(email.user)
        if not net:
            self.error_reporter.report_warning(
                "Unable to determine network for user {!r}".format(email.user)
            )
            return False

        net.send_email(email)
        file.unlink()
        return True
