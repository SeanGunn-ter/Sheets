import re
from .token import Token


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
        if expr.startswith("Sum", i):
            tokens.append(Token("func", "Sum"))
            i += 3
        elif expr.startswith("Concat", i):
            tokens.append(Token("func", "Concat"))
            i += 6
        elif expr.startswith("Max", i):
            tokens.append(Token("func", "Max"))
            i += 3
        elif expr.startswith("Min", i):
            tokens.append(Token("func", "Min"))
            i += 3
        elif expr.startswith("If", i):
            tokens.append(Token("func", "If"))
            i += 2

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
        elif ch in "()":
            tokens.append(Token("paren", ch))
            i += 1

        # Comma
        elif ch == ",":
            tokens.append(Token("comma", ch))
            i += 1

        else:
            raise ValueError(f"Unexpected character '{ch}' at position {i}")

    return tokens
