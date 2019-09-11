import os
import smtplib
from pathlib import Path
from tempfile import NamedTemporaryFile
from textwrap import dedent

import pytest
from mock import patch
from responses import RequestsMock

from mailer.config import SMTPConfig


class MockSMTPConfig(SMTPConfig):
    def send(self, message):
        raise smtplib.SMTPRecipientsRefused([message['To']])


@pytest.fixture()
def mock_smtp_config():
    with patch('mailer.config.SMTPConfig', MockSMTPConfig) as mocked:
        yield mocked


@pytest.fixture()
def mock_api():
    with RequestsMock() as reqs:
        reqs.add(
            'GET', 'https://localhost:8888/api/user?name=nick',
            match_querystring=True,
            json={
                'nc': {
                    'REGSERVER': 'test.example.com',
                }
            }
        )
        yield reqs


@pytest.fixture()
def override_config():
    old = os.getenv('MAILER_CONFIG')
    try:
        os.environ['MAILER_CONFIG'] = 'travis/config.tests.yaml'
        yield
    finally:
        if old is None:
            del os.environ['MAILER_CONFIG']
        else:
            os.environ['MAILER_CONFIG'] = old


def test_invalid_recipient(override_config, mock_smtp_config, mock_api):
    from mailer.daemon import Daemon
    daemon = Daemon()
    with patch.object(daemon.config, 'error_reporter') as reporter:
        with NamedTemporaryFile(delete=False) as tmp:
            tmp.write(dedent("""\
            From: test@example.com
            To: "nick" <a.user@!somedomain.org>

            nick=nick
            type=registration
            code=1234
            """).encode())

        daemon.handle_email(Path(tmp.name))

        reporter.report_warning.assert_called_with(
            "Invalid email recipient(s) ['nick <a.user@!somedomain.org>'], ignoring message"
        )
