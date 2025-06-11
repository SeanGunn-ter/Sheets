class Expr:
    pass


class LiteralInt(Expr):
    def __init__(self, value: int):
        self.value = value

    def evaluate(self, get_value):
        return self.value

    def get_dependencies(self):
        return set()

    def __repr__(self):
        return f"LiteralInt({self.value})"


class CellId(Expr):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, get_value):
        return get_value(self.name)

    def get_dependencies(self):
        return {self.name}

    def __repr__(self):
        return f"CellId({self.name})"


class Plus(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) + self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())

    def __repr__(self):
        return f"Plus({repr(self.left)}, {repr(self.right)})"


class Minus(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) - self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())

    def __repr__(self):
        return f"Minus({repr(self.left)}, {repr(self.right)})"


class Multiply(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) * self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())

    def __repr__(self):
        return f"Multiply({repr(self.left)}, {repr(self.right)})"


class Divide(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) / self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())

    def __repr__(self):
        return f"Divide({repr(self.left)}, {repr(self.right)})"


class Sum(Expr):
    def __init__(self, expr_list):
        self.expr_lst = expr_list

    def evaluate(self, get_value):
        total = 0
        for expr in self.expr_lst:
            total += expr.evaluate(get_value)
        return total

    def get_dependencies(self):
        deps = set()
        for expr in self.expr_lst:
            for dep in expr.get_dependencies():
                deps.add(dep)
        return deps

    def __repr__(self):
        # add
        return f"Sum()"
