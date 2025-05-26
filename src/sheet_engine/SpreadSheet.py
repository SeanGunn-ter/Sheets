import re
from Expression import Expression


class Spreadsheet:
    def __init__(self, size: tuple):  # (col,row)
        self.cells = {}  # stores expr
        self.values = {}
        self.deps = {}  # dependencys dict- if key changes value, all items in set its holding must change
        self.size = size  # tuple (column,row)
        self.evaluate_count = 0

    def set_sheet(self, expr: str) -> None:
        # currently supports 702 columns
        cols, rows = self.size
        first_letter = ""
        second_letter = ""
        x = 0
        loops = 0

        for col in range(cols):
            if x == 0:
                first_letter = chr(col % 26 + 65 + loops)

            if col >= 26:  # passed Z
                second_letter = chr(65 + x)  # restart at A
                x += 1
                if x >= 26:
                    x = 0  # restart second letter to A again
                    loops += 1  # incriment first letter by 1

            letters = first_letter + second_letter

            for row in range(rows):
                self.cells[letters + str(row + 1)] = expr

    def set_cell(self, name: str, expr: str) -> None:
        self.cells[name] = Expression(expr, self)
        self.clear_dependent_values(name)
        self.update_deps(name, expr)

    def get_cell_expr(self, name: str) -> str:
        return self.cells[name]

    def get_cell_value(self, name: str, visited=None) -> int | float:
        if visited is None:
            visited = set()

        if name in self.values:
            return self.values[name]

        expr_obj = self.cells.get(name)
        if not expr_obj:
            # idk
            self.values[name] = 0
            return 0

        value = expr_obj.evaluate(visited)
        self.values[name] = value
        return value

    def clear_dependent_values(self, name):
        if name in self.values:
            self.values.pop(name)
        # recursively remove all values dependent
        for dependent in self.deps.get(name, set()):
            self.clear_dependent_values(dependent)

    def update_deps(self, name: str, expr: str) -> None:
        if expr.startswith("="):
            # set of all dependencys for expr
            dep_set = set(re.findall(r"[A-Z]+\d+", expr))
            for dep in dep_set:
                # add name to deps list (dict where if key changes value, all items in set its holding must change)
                if dep in self.deps:
                    self.deps[dep].add(name)
                else:
                    new_set = set()
                    new_set.add(name)
                    self.deps[dep] = new_set
