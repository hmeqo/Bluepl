"""Terminal simulator.

Usage:
```
import argparse
from ahfakit.apckit.terminalsim import terminal

parser = argparse.ArgumentParser()
parser.add_argument("items", nargs="*")
parser.add_argument("--option", nargs="?")
terminal(print, parser)
```
"""

import sys
import argparse
from typing import Callable, Any


def str_to_args(s):
    """String to sys args."""
    def join_stack():
        if stack:
            args.append("".join(stack))
            stack.clear()

    args = []
    stack = []
    double_quot = False
    escape = False
    for char in s:
        if escape:
            if char not in "\"":
                stack.append("\\")
            stack.append(char)
            escape = False
        elif char == "\\":
            escape = True
        elif char == '"':
            join_stack()
            double_quot = not double_quot
        elif char == " " and not double_quot:
            join_stack()
        else:
            stack.append(char)
    join_stack()
    return double_quot is False and escape is False, args


def terminal(
    callback: Callable[[argparse.Namespace], Any],
    arg_parser: argparse.ArgumentParser,
    exit_code="exit",
    loop=True,
    on_exit: Callable[[], Any] = sys.exit
) -> None:
    """Terminal simulator.
    Callback once when sys.argv length equals 1.
    """
    try:
        if len(sys.argv) == 1:
            arg_parser.print_help()
            while True:
                answer = input(">>> ")
                if not answer:
                    continue
                if answer == exit_code:
                    break
                success, args = str_to_args(answer)
                args, argv = arg_parser.parse_known_args(args, None)
                if not success:
                    print("Error: invalid syntax.")
                elif argv:
                    msg = "Error: unrecognized arguments: %s"
                    print(msg % " ".join(argv))
                else:
                    callback(args)
                if not loop:
                    break
            on_exit()
        else:
            callback(arg_parser.parse_args(sys.argv[1:]))
    except Exception as exc:
        print(exc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("items", nargs="*")
    parser.add_argument("--option", nargs="?")
    terminal(print, parser)


if __name__ == "__main__":
    main()
