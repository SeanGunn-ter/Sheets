from dataclasses import dataclass


@dataclass
class Token:
    type: str  # int, func, op, str, paren, comma
    value: str
