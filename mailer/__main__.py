import time

from .daemon import Daemon
from .message import UserEmail


def main():
    daemon = Daemon()
    while True:
        try:
            daemon.tick()
            mail_file = daemon.get_email_file()
            if not mail_file:
                time.sleep(5)
                continue

            email = UserEmail.from_file(mail_file)
            net = daemon.get_network(email.user)
            if not net:
                daemon.error_reporter.report_warning(
                    "Unable to determine network for user {!r}".format(email.user)
                )
                continue

            net.send_email(email)
            mail_file.unlink()
        except Exception:
            daemon.on_error()
            time.sleep(5)


if __name__ == '__main__':
    main()
