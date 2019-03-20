import email
import sys
import traceback
import uuid
from email.message import Message
from pathlib import Path

script_dir = Path(__file__).resolve().parent
cwd = Path().resolve()


def main():
    if len(sys.argv) > 1:
        mail_dir = sys.argv[1]
    else:
        mail_dir = script_dir / 'emails'

    text = sys.stdin.read()

    mail_dir = Path(mail_dir).resolve()
    msg = email.message_from_string(text)  # type: Message

    file = (mail_dir / '{}.mail'.format(uuid.uuid4()))
    file.touch(0o600)
    with file.open('wb') as f:
        f.write(msg.as_bytes())


def run():
    try:
        main()
    except Exception as e:
        with (script_dir / 'log.txt').open('a', encoding='utf8') as f:
            print(traceback.format_exc(), file=f)

        raise e


if __name__ == '__main__':
    run()
