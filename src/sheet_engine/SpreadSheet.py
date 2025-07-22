from .Expression import Expression


# ToDo
# fix the ErrorFormula logic handeling
# fast name to key func
# copy paste


class Spreadsheet:
    def __init__(self):  # (col,row)
        self.cells = {}  # stores expr obj
        self.values = {}
        # reverse dependency dict- if key changes value, all items in set its holding must change
        self.rev_deps = {}
        self.deps = {}
        self.evaluation_count = 0  # for testing

    def set_cell(self, name: str, expr: str) -> None:
        try:
            self._clear_dependent_values(name)
            self._update_deps(name, expr)
            expr_obj = Expression(expr)
            self.cells[name] = expr_obj
        except ValueError as e:
            self.cells[name] = Expression(str(e))

    def get_cell_expr(self, name: str) -> str:
        return self.cells.get(name, "")

    def get_cell_value(self, name: str) -> int | float:

        if name in self.values:
            return self.values[name]

        self.evaluation_count += 1
        expr = self.cells.get(name)

        if expr is None:
            self.values[name] = f"#ERROR: Cell {name} not found"
            return self.values[name]

        value_dict = self._generate_values(expr)
        value = expr.evaluate(value_dict)
        self.values[name] = value
        return value

    def _clear_dependent_values(self, name: str) -> None:
        if name in self.values:
            self.values.pop(name)
        # recursively remove all values dependent
        for dependent in self.rev_deps.get(name, set()):
            self._clear_dependent_values(dependent)

    def _update_deps(self, name: str, expr: str) -> None:
        try:

            # remove old rev_deps
            old_deps = self.deps.get(name, set())
            for dep in old_deps:
                if name in self.rev_deps.get(dep, set()):
                    self.rev_deps[dep].remove(name)

            expr_obj = Expression(expr)
            dependencies = expr_obj.get_dependencies()
            # re-write deps
            self.deps[name] = dependencies

            if self._has_cycle(name, name, set()):
                raise ValueError("#ERROR Circular dependency detected")

            for dep in dependencies:
                # add name to rev_deps list (dict where if key changes value, all items in set its holding must change)
                if dep in self.rev_deps:
                    self.rev_deps[dep].add(name)
                else:
                    self.rev_deps[dep] = {name}
        except ValueError as e:
            print(f"#ERROR in cell {name}: {e}")
            self.deps[name] = set()
            raise

    def _has_cycle(self, start: str, current: str, visited: set) -> bool:
        if current in visited:
            return False
        visited.add(current)

        for next_cell in self.deps.get(current, set()):
            if next_cell == start:
                return True  # Cycle found!
            if self._has_cycle(start, next_cell, visited):
                return True
        return False

    def _generate_values(self, expr_obj: Expression) -> dict:
        dependencies = expr_obj.get_dependencies()
        value_dict = {}
        for cell in dependencies:
            value_dict[cell] = self.get_cell_value(cell)

        return value_dict


if __name__ == "__main__":
    sheet = Spreadsheet()
    sheet.set_cell("A1", "10")
    sheet.set_cell("B1", "5")
    sheet.set_cell("C1", "=(3*3)+A1+A1+B1")


# python -m src.sheet_engine.SpreadSheet
# python -m src.sheet_engine_ui.spread_sheet_app
