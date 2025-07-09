import re
from .token import Token
from .formula import (
    ALL_FUNCTION_NAMES,
)


def tokenize(expr: str) -> list[Token]:
    tokens = []
    i = 0
    while i < len(expr):
        ch = expr[i]

        # Skip whitespace
        if ch.isspace():
            i += 1
            continue

        # function names
        matched = False
        for name in ALL_FUNCTION_NAMES:
            if expr.startswith(name[0], i):
                tokens.append(Token("func", name[0]))
                i += len(name[0])
                matched = True
                break

        if matched:
            continue

        # Cell
        elif re.match(r"[A-Z]", ch):
            match = re.match(r"[A-Z]+\d+", expr[i:])
            if match:
                tokens.append(Token("cell", match.group()))
                i += len(match.group())
            else:
                raise ValueError(f"Invalid cell reference at position {i}")

        # Integer
        elif ch.isdigit():
            match = re.match(r"\d+", expr[i:])
            tokens.append(Token("int", match.group()))
            i += len(match.group())

        # Op
        elif ch in "+-*/^":
            tokens.append(Token("op", ch))
            i += 1

        # Paren
        elif ch in "(":
            tokens.append(Token("paren_open", ch))
            i += 1

        elif ch in ")":
            tokens.append(Token("paren_close", ch))
            i += 1

        # Comma
        elif ch == ",":
            tokens.append(Token("comma", ch))
            i += 1

        else:
            raise ValueError(f"Unexpected character '{ch}' at position {i}")

    return tokens
