import re
from . import infix_calc
from enum import Enum, auto


class ExpressionType(Enum):
    LITERAL = auto()
    INTEGER = auto()
    FORMULA = auto()


class Expression:
    def __init__(self, expr, value_dict):
        self.expr = expr  # =A1+A2
        self.expr_type = self.determine_type()
        self.deps = value_dict

    def determine_type(self):
        expr = self.expr
        if expr.startswith("="):
            return ExpressionType.FORMULA
        if re.fullmatch(r"\d+", expr):
            return ExpressionType.INTEGER
        else:
            return ExpressionType.LITERAL

    def evaluate(self):
        expr = self.expr
        if self.expr_type == ExpressionType.FORMULA:
            if not infix_calc.has_balanced_parentheses(expr[1:]):
                raise ValueError("Invalid equation")

            split_expr = infix_calc.split(expr[1:])

            split_expr = self.replace_vals(split_expr)

            postfix_expr = infix_calc.infix_postfix(split_expr)

            value = self.postfix_eval(postfix_expr)
            return value
        if self.expr_type == ExpressionType.INTEGER:
            return int(self.expr)

    def replace_vals(self, split_expr):
        for i, cell in enumerate(split_expr):
            if re.fullmatch(r"[A-Z]+\d+", cell):
                split_expr[i] = self.deps[cell]
        return split_expr

    def postfix_eval(self, postfix: list) -> int:
        stack = []
        for item in postfix:
            if isinstance(item, int):
                stack.append(item)
            else:
                b = stack.pop()  # whats pushed first is second operand
                a = stack.pop()
                if item == "+":
                    stack.append(a + b)
                elif item == "-":
                    stack.append(a - b)
                elif item == "*":
                    stack.append(a * b)
                elif item == "/":
                    stack.append(a / b)
                elif item == "^":
                    stack.append(pow(a, b))
        return stack[0]
