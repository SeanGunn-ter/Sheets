import re


def has_balanced_parentheses(expr: str) -> bool:
    stack = []
    for c in expr:
        if c == "(":
            stack.append(c)
        elif c == ")":
            if not stack:
                return False
            stack.pop()
    return not stack


def split(expr: str) -> list:
    return re.findall(r"\d+|[A-Z]+\d+:[A-Z]+\d+|[A-Z]+\d+|[()+\-*/^]", expr)


def split_deps(expr: str) -> list:
    return re.findall(r"[A-Z]+\d+", expr)


def infix_postfix(split_expr: list) -> list:

    postfix = []
    stack = []
    op_dict = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
    for item in split_expr:
        # find stand alone nums or cells
        if isinstance(item, int):
            postfix.append(item)

        elif item in op_dict:
            # While there's an op on the stack with greater or equal value,
            # pop it from the stack and add to the output
            while (
                stack and stack[-1] in op_dict and op_dict[item] <= op_dict[stack[-1]]
            ):
                postfix.append(stack.pop())
            stack.append(item)
        elif item == "(":
            stack.append(item)
        elif item == ")":
            # append until end of parentheis
            while stack and stack[-1] != "(":
                postfix.append(stack.pop())
            stack.pop()  # Remove the '('

    while stack:
        postfix.append(stack.pop())  # append remaining operators in correct order

    return postfix


def postfix_eval(postfix: list) -> int:
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


# split_expr = ["3", "+", "4", "*", "2", "/", "(", "1", "-", "5", ")"]
# print(split_expr)
# print(infix_postfix(split_expr))
# print(split("5+AA11:AA15"))
