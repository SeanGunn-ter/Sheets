import re
from . import infix_calc
from enum import Enum, auto


class ExpressionType(Enum):
    LITERAL = auto()
    INTEGER = auto()
    FORMULA = auto()


class Expression:
    def __init__(self, expr):
        self.expr = expr
        self.expr_type = self._determine_type()

    def _determine_type(self):
        expr = self.expr
        if expr.startswith("="):
            return ExpressionType.FORMULA
        if re.fullmatch(r"\d+", expr):
            return ExpressionType.INTEGER
        else:
            return ExpressionType.LITERAL

    def evaluate(self, value_dict):
        expr = self.expr
        if self.expr_type == ExpressionType.FORMULA:
            if not infix_calc.has_balanced_parentheses(expr[1:]):
                raise ValueError("Invalid equation")

            split_expr = infix_calc.split(expr[1:])

            split_expr = self._replace_vals(split_expr, value_dict)

            postfix_expr = infix_calc.infix_postfix(split_expr)

            value = infix_calc.postfix_eval(postfix_expr)
            return value
        if self.expr_type == ExpressionType.INTEGER:
            return int(expr)

    def _replace_vals(self, split_expr, value_dict):
        for i, cell in enumerate(split_expr):
            if re.fullmatch(r"\d+", cell):
                split_expr[i] = int(cell)
            if re.fullmatch(r"[A-Z]+\d+", cell):
                if cell not in value_dict:
                    raise ValueError(f"Cell {cell} not found in value dict")
                else:
                    split_expr[i] = value_dict[cell]
        return split_expr

    def get_dependencies(self) -> set:
        if self.expr_type != ExpressionType.FORMULA:
            return set()
        return set(re.findall(r"[A-Z]+\d+", self.expr))
