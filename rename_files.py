import argparse
import os
import re
from os import path
from typing import List

import emoji
from termcolor import cprint

"""
Rename all files in selected directories
starting with a regular expression pattern,
replacing all occurences of the pattern at the beginning of the filename
by the replacement repl.
"""


def is_match(filename: str, pattern: str, ext: List[str]) -> bool:
    """
    Check whether a filename starts with a regular expression pattern
    and ends with one of the correct extensions.

    Parameters:
        filename: str
        pattern: str
        ext: List[str]

    Returns:
        True or False
    """
    if ext and filename.lower().split(".")[-1] not in ext:
        return False

    if re.match(pattern, filename):
        return True

    return False


def main(
    dirs: List[str], pattern: str, repl: str, ext: List[str], verbose: bool
) -> None:
    """
    Rename files according to the rule.

    Parameters:
        dirs: List[str]
        pattern: str
        repl: str
        ext: List[str]
        verbose: bool

    Returns:
        None
    """

    count = 0

    for dir_name in dirs:
        filenames = sorted(
            list(
                filter(
                    lambda x: is_match(x, pattern, [x.lower() for x in ext]),
                    os.listdir(dir_name),
                )
            )
        )
        new_filenames = [
            re.sub(pattern, repl, filename, count=1) for filename in filenames
        ]
        if filenames and verbose:
            cprint(dir_name, attrs=["bold"])
        for filename, new_filename in zip(filenames, new_filenames):
            src = path.join(dir_name, filename)
            dst = path.join(dir_name, new_filename)
            os.rename(src, dst)
            if verbose:
                print(
                    emoji.emojize(
                        f":white_check_mark: {filename} -> {new_filename}",
                        use_aliases=True,
                    )
                )
            count += 1
        if filenames and verbose:
            print("\n")

    cprint(
        emoji.emojize("All done! :dizzy: :star2: :dizzy:", use_aliases=True),
        "green",
        attrs=["bold"],
    )

    cprint(
        f"{count} file{'s' if count % 10 != 1 else ''} "
        + f"in {len(dirs)} director{'ies' if len(dirs) % 10 != 1 else 'y'} "
        + "renamed.",
        "green",
        attrs=["bold"],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="rename_files",
        description="Rename all files in selected directories starting with"
        + " a regular expression pattern, replacing all occurences of"
        + " the pattern at the beginning of the filename"
        + " by the replacement repl.",
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
        "-d",
        "--dirs",
        nargs="*",
        default=["."],
        help="paths to directories in which to rename files"
        + " (the current directory by default)",
    )
    parser.add_argument(
        "-e",
        "--ext",
        nargs="*",
        default=[],
        help="extension(s) of files to be renamed;"
        + " only letters and/or numbers (examples: txt, mp3, html);"
        + " if not specified, rename all files",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="increase output verbosity",
    )

    args = parser.parse_args()
    main(args.dirs, args.pattern, args.repl, args.ext, args.verbose)
