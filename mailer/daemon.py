import os
import random
import smtplib
import time
import traceback
from pathlib import Path
from typing import Iterable, List, Union

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

    def get_email_files(self)->List[Path]:
        files = list(self._filter_files(self.mail_dir.rglob('*.mail')))
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
        return 'default'

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

    @staticmethod
    def _filter_files(files:Iterable[Path]):
        for file in files:
            # Wait 30 seconds before reading the file
            if time.time() - file.stat().st_ctime < 30:
                continue

            if file.stat().st_size == 0:
                continue

            yield file
