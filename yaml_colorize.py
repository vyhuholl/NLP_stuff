import argparse
from typing import Generator, List

import yaml
from termcolor import colored, cprint

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader


def tokenize(text: str, loader=SafeLoader) -> Generator[int, int, yaml.Token]:
    """
    A generator for tokenizing a YAML file.
    For each token, yields it, its' start index, and its' end index.

    Parameters:
        text: str
        loader: yaml.Loader

    Yields:
        int
        int
        yaml.Token
    """
    last_token = yaml.ValueToken(None, None)

    for token in yaml.scan(text, loader):
        start = token.start_mark.index
        end = token.end_mark.index
        if isinstance(token, yaml.TagToken):
            yield start, end, token
        elif isinstance(token, yaml.ScalarToken):
            yield start, end, last_token
        elif isinstance(token, (yaml.KeyToken, yaml.ValueToken)):
            last_token = token


def colorize(text: str) -> str:
    """
    Colorizes a YAML file.

    Parameters:
        text: str

    Returns:
        str
    """
    colors = {
        yaml.KeyToken: ["blue", ["bold"]],
        yaml.ValueToken: ["cyan", []],
        yaml.TagToken: ["red", []],
    }

    for start, end, token in reversed(list(tokenize(text))):
        color, attrs = colors[type(token)]
        text = text[:start] + colored(
            text[start:end], color, attrs=attrs
            ) + text[end:]

    return text


def main(files: List[str]) -> None:
    """
    Colorize and print YAML files.

    Parameters:
        files: List[str]

    Returns:
        None
    """
    if len(files) == 1:
        with open(files[0]) as yaml_file:
            print(colorize(yaml_file.read()))
    else:
        for filename in files:
            cprint(filename, attrs=["bold", "underline"])
            with open(filename) as yaml_file:
                print(f"\n{colorize(yaml_file.read())}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="yaml_colorize", description="Print colorized YAML file(s)."
    )

    parser.add_argument("file", nargs="+", help="YAML file(s) to colorize")
    args = parser.parse_args()
    main(args.file)
