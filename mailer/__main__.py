import time

from .daemon import Daemon


def main():
    daemon = Daemon()
    while True:
        daemon.tick()
        files = daemon.get_email_files()
        for file in files:
            try:
                daemon.handle_email(file)
            except Exception:
                daemon.on_error()

        time.sleep(5)


if __name__ == '__main__':
    main()
