from tempfile import NamedTemporaryFile

import pytest


def test_config_template():
    config = {
        'subject': "Test Subject",
        'body': "Test Body",
    }

    from mailer.email_template import EmailTemplate
    tmpl = EmailTemplate.from_config(config)

    assert tmpl.generate({}) == "Subject: Test Subject\n\nTest Body\n"


@pytest.fixture()
def temp_file():
    with NamedTemporaryFile() as f:
        yield f


def test_file_template(temp_file):
    temp_file.write(
        b'Subject: This is a test subject\r\n\r\nTest body\r\n{text}\r\n'
    )
    temp_file.flush()

    config = {'file': temp_file.name}
    from mailer.email_template import EmailTemplate
    tmpl = EmailTemplate.from_config(config)

    expected = 'Subject: This is a test subject\n\nTest body\nfoobar\n'

    assert tmpl.generate({'text': 'foobar'}) == expected
