import re
from enum import Enum, auto
from .expr_types import Expr, LiteralInt, CellId, Plus, Minus, Multiply, Divide


class ExpressionType(Enum):
    LITERAL = auto()
    INTEGER = auto()
    FORMULA = auto()


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
        return ExpressionType.LITERAL

    def evaluate(self, value_dict):
        if self.expr_type == ExpressionType.INTEGER:
            return int(self.expr)
        if self.expr_type == ExpressionType.LITERAL:
            raise ValueError("Can't evaluate yet")

        def get_val(name):
            return value_dict[name]

        return self.tree.evaluate(get_val)

    def get_dependencies(self) -> set:
        if self.expr_type == ExpressionType.FORMULA:
            return self.tree.get_dependencies()
        return set()

    def _parse_expr(self) -> Expr:
        tokens = self._tokenize(self.expr[1:])
        return self._parse_tokens(tokens)

    def _tokenize(self, expr: str):
        return re.findall(r"[A-Z]+\d+|\d+|[+\-*/()]", expr)

    def _parse_tokens(self, tokens: list) -> Expr:
        output = []
        ops = []

        for token in tokens:
            if re.fullmatch(r"\d+", token):
                output.append(LiteralInt(int(token)))
            elif re.fullmatch(r"[A-Z]+\d+", token):
                output.append(CellId(token))
            elif token in "+-*/":
                while (
                    ops and ops[-1] != "(" and precedence(ops[-1]) >= precedence(token)
                ):
                    reduce_stack(output, ops)
                ops.append(token)
            elif token == "(":
                ops.append(token)
            elif token == ")":
                while ops and ops[-1] != "(":
                    reduce_stack(output, ops)
                ops.pop()  # remove )

        while ops:
            reduce_stack(output, ops)

        return output[0]


def precedence(op):
    return {"+": 1, "-": 1, "*": 2, "/": 2}.get(op, 0)


def to_expr(op, left, right):
    return {"+": Plus, "-": Minus, "*": Multiply, "/": Divide}[op](left, right)


def reduce_stack(output, ops):
    op = ops.pop()
    right = output.pop()
    left = output.pop()
    output.append(to_expr(op, left, right))
