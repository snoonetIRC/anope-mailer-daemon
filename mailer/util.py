from datetime import timedelta

intervals = {
    'y': timedelta(days=365.25),
    'w': timedelta(days=7),
    'd': timedelta(days=1),
    'h': timedelta(hours=1),
    'm': timedelta(minutes=1),
    's': timedelta(seconds=1),
}


def parse_interval(text: str) -> timedelta:
    current = ''
    total = timedelta(seconds=0)
    for i, char in enumerate(text):
        if char.isdigit():
            current += char
        elif char in intervals:
            if not current:
                raise ValueError("Missing value at position {}".format(i))

            total += int(current) * intervals[char]
        else:
            raise ValueError("{} is not a valid interval multiplier".format(char))

    if current:
        total += int(current) * intervals['s']

    return total
