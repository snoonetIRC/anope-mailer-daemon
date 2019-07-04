import textwrap
from pathlib import Path
from typing import Any, Dict, Mapping

__all__ = ('EmailTemplate',)

SIMPLE_FMT = """\
Subject: {subject}

{message}
"""


class EmailTemplate:
    def __init__(self, file: Path = None, config: Dict[str, Any] = None):
        if config and file:
            raise TypeError("Only one of 'config' or 'file' can be used")

        if file:
            with file.open(encoding='utf8') as f:
                self.template = f.read()
        else:
            self.template = textwrap.dedent(SIMPLE_FMT).format_map(
                config or {}
            )

    def generate(self, variables: Mapping[str, Any]) -> str:
        return self.template.format_map(variables)

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        file = config.get('file')
        if file:
            return cls(file=Path(file).resolve())

        return cls(config=config)
