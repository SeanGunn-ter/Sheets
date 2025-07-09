from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    INT = auto()
    FUNC = auto()
    OP = auto()
    COMMA = auto()
    PAREN_OPEN = auto()
    PAREN_CLOSE = auto()
    CELL = auto()


@dataclass
class Token:
    type: TokenType  # int, func, op, str, paren, comma
    value: str
