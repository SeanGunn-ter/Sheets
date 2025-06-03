import re
from .Expression import Expression, ExpressionType

from . import infix_calc


class Spreadsheet:
    def __init__(self, size: tuple):  # (col,row)
        self.cells = {}  # stores str expr
        self.values = {}
        # reverse dependency dict- if key changes value, all items in set its holding must change
        self.rev_deps = {}
        self.deps = {}
        self.size = size  # tuple (column,row)
        self.evaluate_count = 0

    def _set_sheet(self, expr: str) -> None:
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
        self._clear_dependent_values(name)

        self._update_deps(name, expr)

        self.cells[name] = expr

    def get_cell_expr(self, name: str) -> str:
        return self.cells[name]

    def get_cell_value(self, name: str) -> int | float:

        if name in self.values:
            return self.values[name]

        expr = self.cells[name]
        value_dict = self._generate_values(expr)

        expr = Expression(expr)
        value = expr.evaluate(value_dict)

        self.values[name] = value
        return value

    def _clear_dependent_values(self, name):
        if name in self.values:
            self.values.pop(name)
        # recursively remove all values dependent
        for dependent in self.rev_deps.get(name, set()):
            self._clear_dependent_values(dependent)

    def _update_deps(self, name: str, expr: str) -> None:
        expr_obj = Expression(expr)
        dependencies = expr_obj.get_dependencies()
        self.deps[name] = dependencies

        if self._has_cycle(name, name, set()):
            raise ValueError("Circular dependency detected")

        if expr_obj.expr_type == ExpressionType.FORMULA:
            for dep in dependencies:
                # add name to rev_deps list (dict where if key changes value, all items in set its holding must change)
                if dep in self.rev_deps:
                    self.rev_deps[dep].add(name)
                else:
                    self.rev_deps[dep] = {name}

    def _has_cycle(self, start, current, visited):
        if current in visited:
            return False
        visited.add(current)

        for next_cell in self.deps.get(current, set()):
            if next_cell == start:
                return True  # Cycle found!
            if self._has_cycle(start, next_cell, visited):
                return True
        return False

    def _generate_values(self, expr):
        # creates a value dict
        dict = {}
        split = infix_calc.split_deps(expr)
        for cell in split:
            # maybe change to int later
            dict[cell] = self.get_cell_value(cell)
        return dict


if __name__ == "__main__":
    sheet = Spreadsheet((10, 10))
    sheet.set_cell("A1", "10")
    sheet.set_cell("B1", "=A1+5")
    sheet.set_cell("C1", "15")

    print(sheet.get_cell_value("B1"))
    sheet.set_cell("A1", "0")
    print(sheet.get_cell_value("B1"))


# python -m src.sheet_engine.SpreadSheet
