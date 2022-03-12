"""
Drop in replacement for `sendmail`
to pass emails to the Anope mailer daemon.
"""
import datetime
import email
import sys
import traceback
import uuid
from email.message import Message
from pathlib import Path

script_dir = Path(__file__).resolve().parent
cwd = Path().resolve()


def main():
    """
    Main function\
    """
    if len(sys.argv) > 1:
        mail_dir = sys.argv[1]
    else:
        mail_dir = script_dir / 'emails'

    text = sys.stdin.read()

    mail_dir = Path(mail_dir).resolve()
    msg = email.message_from_string(text)  # type: Message

    file = (mail_dir / f'{uuid.uuid4()}.mail')
    file.touch(0o600)
    with file.open('w', encoding='utf-8') as file:
        file.write(msg.as_string())


def run():
    """Main wrapper"""
    try:
        main()
    except Exception as err:
        with (script_dir / 'log.txt').open('a', encoding='utf8') as file:
            print(datetime.datetime.now().isoformat(), traceback.format_exc(), file=file)

        raise err


if __name__ == '__main__':
    run()
