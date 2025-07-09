import re
from .token import Token, TokenType
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
                tokens.append(Token(TokenType.FUNC, name[0]))
                i += len(name[0])
                matched = True
                break

        if matched:
            continue

        # Cell
        elif re.match(r"[A-Z]", ch):
            match = re.match(r"[A-Z]+\d+", expr[i:])
            if match:
                tokens.append(Token(TokenType.CELL, match.group()))
                i += len(match.group())
            else:
                raise ValueError(f"Invalid cell reference at position {i}")

        # Integer
        elif ch.isdigit():
            match = re.match(r"\d+", expr[i:])
            tokens.append(Token(TokenType.INT, match.group()))
            i += len(match.group())

        # Op
        elif ch in "+-*/^":
            tokens.append(Token(TokenType.OP, ch))
            i += 1

        # Paren
        elif ch in "(":
            tokens.append(Token(TokenType.PAREN_OPEN, ch))
            i += 1

        elif ch in ")":
            tokens.append(Token(TokenType.PAREN_CLOSE, ch))
            i += 1

        # Comma
        elif ch == ",":
            tokens.append(Token(TokenType.COMMA, ch))
            i += 1

        else:
            raise ValueError(f"Unexpected character '{ch}' at position {i}")

    return tokens
