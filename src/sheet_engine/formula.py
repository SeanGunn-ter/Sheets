from abc import ABC, abstractmethod


class Formula(ABC):
    @abstractmethod
    def evaluate(self, get_value):
        pass

    @abstractmethod
    def get_dependencies(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class LiteralInt(Formula):
    def __init__(self, value: int):
        self.value = value

    def evaluate(self, get_value):
        return self.value

    def get_dependencies(self):
        return set()

    def __repr__(self):
        return f"LiteralInt({self.value})"


class LiteralStr(Formula):
    def __init__(self, value: str):
        self.value = value

    def evaluate(self, get_value):
        return self.value

    def get_dependencies(self):
        return set()

    def __repr__(self):
        return f"LiteralStr({self.value})"


class CellId(Formula):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, get_value):
        return get_value(self.name)

    def get_dependencies(self):
        return {self.name}

    def __repr__(self):
        return f"CellId({self.name})"


class Power(Formula):
    def __init__(self, base: Formula, power: Formula):
        self.base = base
        self.power = power

    def evaluate(self, get_value):
        return self.base.evaluate(get_value) ** self.power.evaluate(get_value)

    def get_dependencies(self):
        return self.base.get_dependencies().union(self.power.get_dependencies())

    def __repr__(self):
        return f"Power({repr(self.base)}, {repr(self.power)})"


class Plus(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) + self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())

    def __repr__(self):
        return f"Plus({repr(self.left)}, {repr(self.right)})"


class Minus(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) - self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())

    def __repr__(self):
        return f"Minus({repr(self.left)}, {repr(self.right)})"


class Multiply(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) * self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())

    def __repr__(self):
        return f"Multiply({repr(self.left)}, {repr(self.right)})"


class Divide(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def evaluate(self, get_value):
        return self.left.evaluate(get_value) / self.right.evaluate(get_value)

    def get_dependencies(self):
        return self.left.get_dependencies().union(self.right.get_dependencies())

    def __repr__(self):
        return f"Divide({repr(self.left)}, {repr(self.right)})"


class Sum(Formula):
    def __init__(self, formula_lst):
        self.formula_lst = formula_lst

    def evaluate(self, get_value):
        total = 0
        for Formula in self.formula_lst:
            total += Formula.evaluate(get_value)
        return total

    def get_dependencies(self):
        deps = set()
        for Formula in self.formula_lst:
            for dep in Formula.get_dependencies():
                deps.add(dep)
        return deps

    def __repr__(self):
        inner = ""
        for i, Formula in enumerate(self.formula_lst):
            if i > 0:
                inner += ", "
            inner += repr(Formula)
        return f"Sum({inner})"


class Concat(Formula):
    def __init__(self, formula_lst):
        self.formula_lst = formula_lst

    def evaluate(self, get_value):
        result = ""
        for expr in self.formula_lst:
            result += str((expr.evaluate(get_value)))
        return result

    def get_dependencies(self):
        deps = set()
        for expr in self.formula_lst:
            deps.update(expr.get_dependencies())
        return deps

    def __repr__(self):
        inner = ""
        for i, Formula in enumerate(self.formula_lst):
            if i > 0:
                inner += ", "
            inner += repr(Formula)
        return f"Concat({inner})"


class Max(Formula):
    def __init__(self, formula_lst):
        self.formula_lst = formula_lst

    def evaluate(self, get_value):
        return max(expr.evaluate(get_value) for expr in self.formula_lst)

    def get_dependencies(self):
        deps = set()
        for expr in self.formula_lst:
            deps.update(expr.get_dependencies())
        return deps

    def __repr__(self):
        inner = ""
        for i, Formula in enumerate(self.formula_lst):
            if i > 0:
                inner += ", "
            inner += repr(Formula)
        return f"Max({inner})"


class Min(Formula):
    def __init__(self, formula_lst):
        self.formula_lst = formula_lst

    def evaluate(self, get_value):
        return min(expr.evaluate(get_value) for expr in self.formula_lst)

    def get_dependencies(self):
        deps = set()
        for expr in self.formula_lst:
            deps.update(expr.get_dependencies())
        return deps

    def __repr__(self):
        inner = ""
        for i, Formula in enumerate(self.formula_lst):
            if i > 0:
                inner += ", "
            inner += repr(Formula)
        return f"Min({inner})"


class If(Formula):
    def __init__(self, formula_lst):
        self.condition = formula_lst[0]
        self.then_expr = formula_lst[1]
        self.else_expr = formula_lst[2]

    def evaluate(self, get_value):
        cond = self.condition.evaluate(get_value)
        return (
            self.then_expr.evaluate(get_value)
            if cond
            else self.else_expr.evaluate(get_value)
        )

    def get_dependencies(self):
        return (
            self.condition.get_dependencies()
            .union(self.then_expr.get_dependencies())
            .union(self.else_expr.get_dependencies())
        )

    def __repr__(self):
        return f"If({repr(self.condition)}, {repr(self.then_expr)}, {repr(self.else_expr)})"


ALL_FUNCTION_NAMES = [
    ("If", If),
    ("Sum", Sum),
    ("Concat", Concat),
    ("Max", Max),
    ("Min", Min),
]
