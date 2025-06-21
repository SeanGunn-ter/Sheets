import re
from .formula import (
    Formula,
    LiteralInt,
    CellId,
    Minus,
    Multiply,
    Divide,
    Sum,
    If,
    Concat,
    Max,
    Min,
)


def tokenize(expr: str):
    return re.findall(r"Sum|Concat|Max|Min|If|[A-Z]+\d+|\d+|[+\-*/(),]", expr)


def parse_expr(expr: str) -> Formula:
    tokens = tokenize(expr)
    return parse_tokens(tokens)


def parse_tokens(tokens: list) -> Formula:
    output = []
    ops = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if re.fullmatch(r"\d+", token):
            output.append(LiteralInt(int(token)))
            i += 1
        elif re.fullmatch(r"[A-Z]+\d+", token):
            output.append(CellId(token))
            i += 1
        elif token in {"Sum", "If", "Concat", "Max", "Min"}:
            func_expr, i = _parse_func_call(tokens, i, token)
            output.append(func_expr)
        elif token in "+-*/":
            while ops and ops[-1] != "(" and _precedence(ops[-1]) >= _precedence(token):
                _reduce_stack(output, ops)
            ops.append(token)
            i += 1
        elif token == "(":
            ops.append(token)
            i += 1
        elif token == ")":
            while ops and ops[-1] != "(":
                _reduce_stack(output, ops)
            if not ops or ops[-1] != "(":
                raise ValueError("Mismatched parentheses")
            ops.pop()
            i += 1
        else:
            raise ValueError(f"Unexpected token: {token}")

    while ops:
        _reduce_stack(output, ops)

    if not output:
        raise ValueError("Empty expression")

    return output[0]


def _reduce_stack(output, ops):
    # postfix to Formula
    op = ops.pop()
    right = output.pop()
    left = output.pop()
    output.append(_to_expr(op, left, right))


def _precedence(op):
    return {"+": 1, "-": 1, "*": 2, "/": 2}.get(op, 0)


def _to_expr(op, left, right):
    if op == "+":
        parts = []

        # extend Sum() formula if possible
        def collect(expr):
            if isinstance(expr, Sum):
                parts.extend(expr.formula_lst)
            else:
                parts.append(expr)

        collect(left)
        collect(right)
        return Sum(parts)

    return {"-": Minus, "*": Multiply, "/": Divide}[op](left, right)


# finds index where arg ends
def _find_argument_end(tokens, start):
    depth = 0
    i = start
    while i < len(tokens):
        t = tokens[i]
        if t == "(":
            depth += 1
        elif t == ")":
            if depth == 0:
                return i
            depth -= 1
        elif t == "," and depth == 0:
            return i
        i += 1
    return i


def _parse_func_call(tokens, i, func_name):
    if i + 1 >= len(tokens) or tokens[i + 1] != "(":
        raise ValueError(f"Expected '(' after function name '{func_name}'")

    i += 2  # skip function name and '('
    args = []
    expecting_arg = True
    done = False

    while i < len(tokens) and not done:
        token = tokens[i]

        if token == ")":
            done = True
            i += 1
        elif expecting_arg:
            end = _find_argument_end(tokens, i)
            sub_expr = parse_tokens(tokens[i:end])
            args.append(sub_expr)
            i = end
            expecting_arg = False
        else:
            if token == ",":
                i += 1
                expecting_arg = True
            else:
                raise ValueError(f"Expected ',' or ')' after argument, got '{token}'")

    if not done:
        raise ValueError("Expected ')' to close function call")

    if func_name == "Sum":
        return Sum(args), i
    elif func_name == "Concat":
        return Concat(args), i
    elif func_name == "Max":
        return Max(args), i
    elif func_name == "Min":
        return Min(args), i
    elif func_name == "If":
        if len(args) != 3:
            raise ValueError("If expects 3 arguments")
        return If(args[0], args[1], args[2]), i
    else:
        raise ValueError(f"Unknown function '{func_name}'")
