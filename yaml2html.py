import argparse
from typing import Generator, Iterable, List, Optional

import yaml
from termcolor import colored, cprint
from yaml import (
    ScalarEvent,
    SequenceStartEvent,
    SequenceEndEvent,
    MappingStartEvent,
    MappingEndEvent,
    DocumentEndEvent
    )

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

OPEN_TAG_EVENTS = (ScalarEvent, SequenceStartEvent, MappingStartEvent)
CLOSE_TAG_EVENTS = (ScalarEvent, SequenceEndEvent, MappingEndEvent)


class HTMLBuilder:
    """Builds HTML of a sequence of events from a YAML file."""

    def __init__(self):
        self._context = []
        self._html = []

    def _color(
        self, tag: str, color: str = "magenta",
        attrs: Optional[Iterable[str]] = ["blink"]
            ) -> str:
        """
        Colorizes a HTML tag.

        Parameters:
            tag: str
            color: str = "magenta"
            attrs: Optional[Iterable[str]] = ["blink"]

        Returns:
            str
        """
        return colored(tag, color, attrs=attrs)

    @property
    def html(self) -> str:
        """HTML tags and their content, processed so far."""
        return "".join(self._html)

    def _handle_tag(self, close: bool = False) -> None:
        """
        Open or close matching tags when necessary.

        Parameters:
            close: bool = False

        Returns:
            None
        """
        if len(self._context) > 0:
            if self._context[-1] == "list":
                self._html.append(
                    self._color("</li>") if close else self._color("<li>")
                    )
            else:
                if self._context[-1] % 2 == 0:
                    self._html.append(
                        self._color("</dt>") if close else self._color("<dt>")
                        )
                else:
                    self._html.append(
                        self._color("</dd>") if close else self._color("<dd>")
                        )
                if close:
                    self._context[-1] += 1

    def process(self, event: yaml.Event) -> None:
        """
        Process an event.

        Parameters:
            event: yaml.Event

        Returns:
            None
        """
        if isinstance(event, OPEN_TAG_EVENTS):
            self._handle_tag()
            if isinstance(event, ScalarEvent):
                self._html.append(event.value)
            elif isinstance(event, SequenceStartEvent):
                self._html.append(self._color("<ul>"))
                self._context.append("list")
            elif isinstance(event, MappingStartEvent):
                self._html.append(self._color("<dl>"))
                self._context.append(0)
        if isinstance(event, CLOSE_TAG_EVENTS):
            self._handle_tag(close=True)
            if isinstance(event, SequenceEndEvent):
                self._html.append(self._color("</ul>"))
                self._context.pop()
            elif isinstance(event, MappingEndEvent):
                self._html.append(self._color("</dl>"))
                self._context.pop()


def yaml2html(stream: str, loader=SafeLoader) -> Generator[str, None, None]:
    """
    A generator for parsing a stream of events from a YAML file
    and translating it to HTML.

    Parameters:
        str: str
        loader: yaml.Loader = SafeLoader

    Yields:
        str
    """
    builder = HTMLBuilder()

    for event in yaml.parse(stream, loader):
        builder.process(event)
        if isinstance(event, DocumentEndEvent):
            yield builder.html
            builder = HTMLBuilder()


def main(files: List[str]) -> None:
    """
    Convert YAML file(s) to HTML.

    Parameters:
        files: List[str]

    Returns:
        None
    """
    if len(files) == 1:
        with open(files[0]) as yaml_file:
            print("".join(yaml2html(yaml_file.read())))
    else:
        for filename in files:
            cprint(filename, attrs=["bold", "underline"])
            with open(filename) as yaml_file:
                print(f"\n{''.join(yaml2html(yaml_file.read()))}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="yaml2html", description="Convert YAML file(s) to HTML."
    )

    parser.add_argument("file", nargs="+", help="YAML file(s) to convert")
    args = parser.parse_args()
    main(args.file)
