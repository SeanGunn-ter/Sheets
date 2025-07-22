from .tokenizer import tokenize
from .token import Token, TokenType
from .formula import (
    Formula,
    LiteralInt,
    CellId,
    Minus,
    Multiply,
    Divide,
    Sum,
    Power,
    ErrorFormula,
    Equal,
    ALL_FUNCTION_NAMES,
)


def parse_expr(expr: str) -> Formula:
    try:
        tokens = tokenize(expr)
        return parse_tokens(tokens)

    except ValueError as e:
        print(f"[parse_expr] Error: {e}")
        return ErrorFormula(str(e))


def parse_tokens(tokens: list[Token]) -> Formula:
    try:
        output = []
        ops = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            match (token.type):
                case TokenType.INT:
                    output.append(LiteralInt(int(token.value)))
                    i += 1
                case TokenType.CELL:
                    output.append(CellId(token.value))
                    i += 1
                case TokenType.FUNC:
                    func_expr, i = _parse_func_call(tokens, i, token.value)
                    output.append(func_expr)
                case TokenType.OP:
                    while (
                        ops
                        and ops[-1].type != "paren"
                        and _precedence(ops[-1].value) >= _precedence(token.value)
                    ):
                        _reduce_stack(output, ops)
                    ops.append(token)
                    i += 1
                case TokenType.PAREN_OPEN:
                    ops.append(token)
                    i += 1
                case TokenType.PAREN_CLOSE:
                    while ops and (ops[-1].type != TokenType.PAREN_OPEN):
                        _reduce_stack(output, ops)
                    if not ops or (
                        ops[-1].type != TokenType.PAREN_OPEN and ops[-1].value == "("
                    ):
                        raise ValueError("Mismatched parentheses")
                    ops.pop()
                    i += 1
                case TokenType.COMMA:
                    i += 1  # handled in _parse_func_call
                case _:
                    raise ValueError(f"Unexpected token: {token}")

        while ops:
            _reduce_stack(output, ops)

        if not output:
            raise ValueError("Empty expression")

        return output[0]

    except ValueError as e:
        print(f"[parse_tokens] Error: {e}")
        return LiteralInt(0)


def _reduce_stack(output, ops):
    # postfix to Formula
    op = ops.pop().value
    right = output.pop()
    left = output.pop()
    output.append(_to_expr(op, left, right))


def _precedence(op):
    return {"=": 0, "+": 1, "-": 1, "*": 2, "/": 2, "^": 3}.get(op, 0)


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

    return {"-": Minus, "*": Multiply, "/": Divide, "^": Power, "=": Equal}[op](
        left, right
    )


# finds index where arg ends
def _find_argument_end(tokens, start):
    depth = 0
    i = start
    while i < len(tokens):
        t = tokens[i].value
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
    try:
        if i + 1 >= len(tokens) or tokens[i + 1].value != "(":
            raise ValueError(f"Expected '(' after function name '{func_name}'")

        i += 2  # skip function name and '('
        args = []
        expecting_arg = True
        done = False

        while i < len(tokens) and not done:
            token = tokens[i]

            if token.type == TokenType.PAREN_CLOSE:
                done = True
                i += 1
            elif expecting_arg:
                end = _find_argument_end(tokens, i)
                sub_expr = parse_tokens(tokens[i:end])
                args.append(sub_expr)
                i = end
                expecting_arg = False
            else:
                if token.type == TokenType.COMMA:
                    i += 1
                    expecting_arg = True
                else:
                    raise ValueError(
                        f"Expected ',' or ')' after argument, got '{token}'"
                    )

        if not done:
            raise ValueError("Expected ')' to close function call")

        for name, cls in ALL_FUNCTION_NAMES:
            if func_name == name:
                return cls(args), i

        raise ValueError(f"Unknown function '{func_name}'")
    except ValueError as e:
        print(f"[parse_func_call] Error: {e}")
        return LiteralInt(0), len(tokens)  # fallback formula and safe index
