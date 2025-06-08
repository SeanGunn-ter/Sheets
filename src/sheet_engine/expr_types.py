class Expr:
    pass


class LiteralInt(Expr):
    def __init__(self, value: int):
        self.value = value

    def evaluate(self, get_value):
        return self.value

    def get_dependencies(self):
        return set()


class CellId(Expr):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, get_value):
        return get_value(self.name)

    def get_dependencies(self):
        return {self.name}


class Plus(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) + self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())


class Minus(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) - self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())


class Multiply(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) * self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())


class Divide(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) / self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())
