from datetime import datetime
from email.message import EmailMessage
from typing import TYPE_CHECKING

from .util import parse_interval

if TYPE_CHECKING:
    from .daemon import Daemon


class Reporter:
    def __init__(self, config, core: 'Daemon'):
        self.core = core
        self.smtp_config = config.get('smtp')
        self.email = config.get('to')
        self.delay = parse_interval(config.get('delay'))

        self.last_send = datetime.min

    @property
    def can_send(self):
        return (datetime.now() - self.last_send) > self.delay

    def send_message(self, subject, body):
        self.last_send = datetime.now()

        if not self.smtp_config:
            return

        message = EmailMessage()
        message['To'] = self.email
        message['Subject'] = subject
        message.set_payload(body)

        self.core.send_message(self.smtp_config, message)

    def tick(self):
        pass


class ErrorReporter(Reporter):
    def __init__(self, config, core):
        super().__init__(config, core)
        self.errors = []
        self.warnings = []

    @property
    def has_to_send(self):
        return bool(self.errors or self.warnings)

    def report_error(self, error_message):
        self.errors.append((datetime.utcnow(), error_message))

    def report_warning(self, message):
        self.warnings.append((datetime.utcnow(), message))

    def make_section(self, title, messages, sep='-' * 24):
        lines = ["{}:".format(title)]
        for at, message in messages:
            lines.append(sep)
            lines.append('')
            lines.append("At: {:%c}".format(at))
            lines.append('')
            lines.append(message)
            lines.append('')

        lines.append(sep)
        return '\n'.join(lines) + '\n'

    def tick(self):
        super().tick()
        if not self.can_send or not self.has_to_send:
            return

        counts = []
        if self.errors:
            counts.append('{} Errors'.format(len(self.errors)))

        if self.warnings:
            counts.append('{} Warnings'.format(len(self.warnings)))

        subject = "maild Status Report - {}".format(
            ', '.join(counts)
        )

        body = ""

        if self.warnings:
            body += self.make_section("Warnings", self.warnings)

        if self.errors:
            body += self.make_section("Errors", self.errors)

        self.warnings.clear()
        self.errors.clear()

        self.send_message(subject, body)
