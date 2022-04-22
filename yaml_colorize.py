import argparse
from typing import Generator, List, Tuple, Type, Union

import yaml
from termcolor import colored, cprint

try:
    from yaml import (
        CSafeLoader as SafeLoader,
        CUnsafeLoader as UnsafeLoader,
        CFullLoader as FullLoader,
        )
except ImportError:
    from yaml import SafeLoader, UnsafeLoader, FullLoader


def tokenize(
    text: str, loader: Union[
        Type[yaml.CSafeLoader],  Type[yaml.SafeLoader],
        Type[yaml.CUnsafeLoader],  Type[yaml.UnsafeLoader],
        Type[yaml.CFullLoader],  Type[yaml.FullLoader]
    ] = SafeLoader
        ) -> Generator[
            Tuple[
                int, int, Union[yaml.KeyToken, yaml.TagToken, yaml.ValueToken]
                ], None, None
            ]:
    """
    A generator for tokenizing a YAML file.
    For each token, yields it, its' start index, and its' end index.

    Parameters:
        text: str
        loader: one of yaml loader types, default SafeLoader

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


def colorize(
    text: str, loader: Union[
        Type[yaml.CSafeLoader],  Type[yaml.SafeLoader],
        Type[yaml.CUnsafeLoader],  Type[yaml.UnsafeLoader],
        Type[yaml.CFullLoader],  Type[yaml.FullLoader]
    ] = SafeLoader
        ) -> str:
    """
    Colorizes a YAML file.

    Parameters:
        text: str
        loader: one of yaml loader types, default SafeLoader

    Returns:
        str
    """
    colors = {
        yaml.KeyToken: "blue",
        yaml.ValueToken: "cyan",
        yaml.TagToken: "red"
    }

    for start, end, token in reversed(list(tokenize(text, loader=loader))):
        color = colors[type(token)]
        attrs = ["bold"] if isinstance(token, yaml.KeyToken) else None
        text = text[:start] + colored(
            text[start:end], color, attrs=attrs
            ) + text[end:]

    return text


def main(files: List[str], loader: str) -> None:
    """
    Colorize and print YAML files.

    Parameters:
        files: List[str]
        loader: str

    Returns:
        None
    """
    loaders = {"safe": SafeLoader, "unsafe": UnsafeLoader, "full": FullLoader}

    if len(files) == 1:
        with open(files[0]) as yaml_file:
            text = yaml_file.read()
            print(colorize(text, loader=loaders[loader]))
    else:
        for filename in files:
            cprint(filename, attrs=["bold", "underline"])
            with open(filename) as yaml_file:
                text = yaml_file.read()
                print(f"\n{colorize(text, loader=loaders[loader])}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="yaml_colorize", description="Print colorized YAML file(s)."
    )

    parser.add_argument("file", nargs="+", help="YAML file(s) to colorize")

    parser.add_argument(
        "-l", "--loader", default="safe", choices=["safe", "unsafe", "full"],
        help="a PyYAML loader to use, default is 'safe'"
        )

    args = parser.parse_args()
    main(args.file, args.loader)
