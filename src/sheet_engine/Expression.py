import re
from enum import Enum, auto
from .parser import parse_expr
from .formula import Formula


class ExpressionType(Enum):
    LITERAL = auto()
    INTEGER = auto()
    FORMULA = auto()
    ERROR = auto()


class Expression:
    def __init__(self, expr):
        self.expr = expr
        self.expr_type = self._determine_type()
        self.tree = (
            self._parse_expr() if self.expr_type == ExpressionType.FORMULA else None
        )

    def _determine_type(self):
        if self.expr.startswith("="):
            return ExpressionType.FORMULA
        if re.fullmatch(r"\d+", self.expr):
            return ExpressionType.INTEGER
        if self.expr.startswith("#ERROR"):
            return ExpressionType.ERROR
        return ExpressionType.LITERAL

    def evaluate(self, value_dict):
        if self.expr_type == ExpressionType.INTEGER:
            return int(self.expr)
        if self.expr_type == ExpressionType.LITERAL:
            return self.expr
        if self.expr_type == ExpressionType.ERROR:
            return self.expr

        def get_val(name):
            return value_dict[name]

        return self.tree.evaluate(get_val)

    def get_dependencies(self) -> set:
        if self.expr_type == ExpressionType.FORMULA:
            return self.tree.get_dependencies()
        return set()

    def _parse_expr(self) -> Formula:
        return parse_expr(self.expr[1:])
