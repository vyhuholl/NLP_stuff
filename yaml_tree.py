import argparse
from typing import List, Type, Union

import yaml
from yaml import ScalarNode, SequenceNode, MappingNode

try:
    from yaml import (
        CSafeLoader as SafeLoader,
        CUnsafeLoader as UnsafeLoader,
        CFullLoader as FullLoader,
        )
except ImportError:
    from yaml import SafeLoader, UnsafeLoader, FullLoader


def html_element(node: List[str]) -> str:
    """
    Parses a scalar node in a YAML tree
    and returns the corresponding HTML element.

    Parameters:
        node: List[str]

    Returns:
        str
    """

    match node:
        case [tag, _] if tag.endswith(":binary"):
            return f'<img src="data:image/png;base64, {node[1]}" />'
        case [_, value] if "\n" in value:
            return f'<div class="multiline">{node[1]}</div>'
        case _:
            return f"<span>{node[1]}</span>"


def html_list(node: SequenceNode) -> str:
    """
    Parses a sequence node in a YAML tree
    and returns the corresponding HTML list.

    Parameters:
        node: SequenceNode

    Returns:
        str
    """
    new = "\n"

    return f'''<ul class="sequence">
    {new.join([f"<li>{visit(child)}</li>" for child in node.value])}
    </ul>'''


def html_map(node: MappingNode) -> str:
    """
    Parses a mapping node in a YAML tree
    and returns the corresponding HTML map.

    Parameters:
        node: MappingNode

    Returns:
        str
    """
    new = "\n"

    return f"""<ul>
    {new.join([f'''<li>
    <span class="key">{visit(key)}:</span> {visit(value)}
    </li>'''
    if isinstance(value, ScalarNode) else f'''<li>
    <details>
    <summary class="key">{visit(key)}</summary> {visit(value)}
    </details>
    </li>''' for key, value in node.value])}
    </ul>"""


def visit(
    node: Union[ScalarNode, SequenceNode, MappingNode],
    loader: Union[
        Type[yaml.CSafeLoader],  Type[yaml.SafeLoader],
        Type[yaml.CUnsafeLoader],  Type[yaml.UnsafeLoader],
        Type[yaml.CFullLoader],  Type[yaml.FullLoader]
    ] = SafeLoader
        ) -> str:
    """
    Visits one node in a YAML tree and returns the corresponding HTML.

    Parameters:
        node: Union[ScalarNode, SequenceNode, MappingNode]
        loader: one of yaml loader types, default SafeLoader

    Returns:
        str
    """

    if isinstance(node, ScalarNode):
        return html_element([node.tag, node.value])
    elif isinstance(node, SequenceNode):
        return html_list(node)
    elif isinstance(node, MappingNode):
        return html_map(node)


def parse(
    filename: str, loader: Union[
        Type[yaml.CSafeLoader],  Type[yaml.SafeLoader],
        Type[yaml.CUnsafeLoader],  Type[yaml.UnsafeLoader],
        Type[yaml.CFullLoader],  Type[yaml.FullLoader]
    ] = SafeLoader
        ) -> str:
    """
    Parses a YAML file as a tree (starting from the root node)
    and returns the corresponding HTML.

    Parameters:
        filename: str
        loader: one of yaml loader types, default SafeLoader

    Returns:
        str
    """

    with open(filename) as yaml_file:
        html = visit(yaml.compose(yaml_file.read(), loader))

    return html


def main(files: List[str], output_file: str, loader: str) -> None:
    """
    Visialise YAML file(s) as a tree and store the result as a HTML file.

    Parameters:
        files: List[str]
        loader = str
        output_file: str

    Returns:
        None
    """
    loaders = {"safe": SafeLoader, "unsafe": UnsafeLoader, "full": FullLoader}

    head = """<meta charset=\"utf-8\">
    <title>YAML Tree Preview</title>
    <link href=\"https://fonts.googleapis.com/css2
    ?family=Roboto+Condensed&display=swap\" rel=\"stylesheet\">
    <style>
      * { font-family: 'Roboto Condensed', sans-serif; }
      ul { list-style: none; }
      ul.sequence { list-style: '- '; }
      .key { font-weight: bold; }
      .multiline { white-space: pre; }
    </style>"""

    new = "\n"

    with open(output_file, "w") as html_file:
        if len(files) == 1:
            html_file.write(
                f"""<!DOCTYPE html>
                <html>
                <head>
                {head}
                </head>
                <body>
                {parse(files[0], loaders[loader])}
                </body>
                """
                )
        else:
            html_file.write(
                f"""<!DOCTYPE html>
                <html>
                <head>
                {head}
                </head>
                <body>
                {new.join([
                    f'<h1>{name}</h1>{new}{parse(name, loaders[loader])}'
                    for name in files
                    ])}
                </body>
                """
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="yaml_tree",
        description="Visialise YAML file(s) as an interactible tree \
            and store the result in a HTML file."
    )

    parser.add_argument(
        "file", nargs="+", help="YAML file(s) to visualize as a tree"
    )

    parser.add_argument("-o", "--output", required=True, help="output file")

    parser.add_argument(
        "-l", "--loader", default="safe", choices=["safe", "unsafe", "full"],
        help="a PyYAML loader to use, default is 'safe'"
    )

    args = parser.parse_args()
    main(args.file, args.output, args.loader)
