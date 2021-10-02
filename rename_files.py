import argparse
import os
import re
from os import path
from typing import List

"""
Rename all files in a directory starting with a regular expression pattern,
replacing all occurences of the pattern at the beginning of the filename
by the replacement repl.
"""


def main(dir_name: str, pattern: str, repl: str, ext: List[str]) -> None:
    """
    Rename files according to the rule.

    Parameters:
        dir_name: str
        pattern: str
        repl: str
        ext: List

    Returns:
        None
    """
    files = sorted(
        list(
            filter(
                lambda x: x.lower().split(".")[-1] in ext if ext else True,
                os.listdir(dir_name),
            )
        )
    )
    count = 0
    for filename in files:
        if re.match(pattern, filename):
            new_filename = re.sub(pattern, repl, filename, count=1)
            src = path.join(dir_name, filename)
            dst = path.join(dir_name, new_filename)
            os.rename(src, dst)
            count += 1
    print(f"All done!\n{count} file{'s' if count % 10 != 1 else ''} renamed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="rename_files",
        description="Rename all files in a directory starting with"
        + " a regular expression pattern, replacing all occurences of"
        + " the pattern at the beginning of the filename"
        + " by the replacement repl.",
    )
    parser.add_argument(
        "dir_name",
        nargs="?",
        default=".",
        help="directory in which to rename files"
        + " (the current directory by default)",
    )
    parser.add_argument(
        "pattern",
        nargs="?",
        default="",
        help="regular expression pattern to replace"
        + " at the beginning of the filename (empty string by default)",
    )
    parser.add_argument(
        "repl",
        nargs="?",
        default="",
        help="replacement string (empty string by default)",
    )
    parser.add_argument(
        "-e",
        "--ext",
        nargs="*",
        default=[],
        help="extension(s) of files to be renamed;"
        + " lowercase, only letters and/or numbers (examples: txt, mp3, html);"
        + " if not specified, rename all files",
    )
    args = parser.parse_args()
    main(args.dir_name, args.pattern, args.repl, args.ext)
