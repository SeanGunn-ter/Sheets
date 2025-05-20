import re
import infix_calc


class Spreadsheet:
    def __init__(self, size: tuple):  # (col,row)
        self.cells = {}  # stores expr
        self.values = {}
        self.deps = (
            {}
        )  # dependencys dict- if key changes value, all items in set its holding must change
        self.size = size  # tuple (column,row)

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
        self.cells[name] = expr
        if name in self.values:  # delete old value
            self.values.pop(name)

        if name in self.deps:
            for item in self.deps[name]:

                if (
                    item in self.values
                ):  # deletes values of all cells dependent on current cell, meaning they have to be reretrieved, when get_cell_value is called
                    self.values.pop(item)

        self.update_deps(
            name, expr
        )  # add to how new other cells depenedend on curr expr

    def get_cell_expr(self, name: str) -> str:
        return self.cells[name]

    def get_cell_value(self, name: str) -> int | float:
        return self.evaluate(name, set())

    def evaluate(self, name: str, visited: set) -> int:

        if name in visited:
            raise ValueError("Circular dependency detected")
        visited.add(name)

        expr = self.cells.get(name, "0")
        if expr.startswith("="):
            if ":" in expr:
                expanded_exprs = col_expanded_operation(expr)
                for i, e in enumerate(expanded_exprs):
                    if not infix_calc.has_balanced_parentheses(e[1:]):
                        raise ValueError("Invalid equation")
                    split_expr = infix_calc.split(e)
                    postfix_expr = infix_calc.infix_postfix(split_expr)
                    value = self.postfix_eval(postfix_expr, visited)

                    match = re.match(r"([A-Z]+)(\d+)", name)

                    col, row = match.groups()
                    new_row = int(row) + i
                    new_name = f"{col}{new_row}"
                    # auto updates deps for new col
                    self.set_cell(new_name, e)
                    self.cells[new_name] = e

                    # add to deps for cur cell
                    if name in self.deps:
                        self.deps[name].add(new_name)
                    elif name != new_name:
                        new_set = set()
                        new_set.add(new_name)
                        self.deps[name] = new_set
                        self.deps[name].add(new_name)

                    self.values[new_name] = value

            else:

                if not infix_calc.has_balanced_parentheses(expr[1:]):
                    raise ValueError("Invalid equation")
                split_expr = infix_calc.split(expr[1:])
                postfix_expr = infix_calc.infix_postfix(split_expr)
                # recursevely calls evaluate, adding to visted, making sure circular dependencys dont exist
                value = self.postfix_eval(postfix_expr, visited)

                self.values[name] = value
        else:
            if re.fullmatch(r"\d+", expr):
                self.values[name] = int(expr)
            else:
                self.values[name] = expr
        visited.remove(name)

        return self.values[name]

    # need to update for col ops
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

    def postfix_eval(self, postfix: list, visited) -> int:
        stack = []
        for item in postfix:
            if re.fullmatch(r"\d+", item):  # num
                stack.append(int(item))
            elif re.fullmatch(r"[A-Z]+\d+", item):  # cell name
                val = self.evaluate(item, visited)
                stack.append(val)
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


def col_expanded_operation(expr):
    matches = re.findall(r"([A-Z]+)(\d+):\1(\d+)", expr)
    # print(matches)
    if not matches:
        return [expr]  # No ranges to expand

    # creates list of each var instance in range, (A1:A2 = [A1,A2])
    expanded_columns = []
    for col, start, end in matches:
        start, end = int(start), int(end)
        if end < start:
            start, end = end, start  # reverse range
        expanded_columns.append([f"{col}{i}" for i in range(start, end + 1)])
    if check_ranges(expanded_columns) == False:
        raise ValueError("Ranges dont match")
    expr_lst = []
    for i in range(len(expanded_columns[0])):
        modified_expr = expr
        # zip matches and expanded columns
        for (col, start, end), replacements in zip(
            matches, expanded_columns
        ):  # [(("A","1","5"),["A1","A2","A3","A4","A5"])]
            pattern = f"{col}{start}:{col}{end}"
            modified_expr = modified_expr.replace(pattern, replacements[i])
            modified_expr = "=" + modified_expr
        expr_lst.append(modified_expr)
    return expr_lst


def check_ranges(expr) -> bool:
    len_r = len(expr[0])
    for e in expr:
        if len(e) != len_r:
            return False
    return True


sheet = Spreadsheet((10, 10))
sheet.set_cell("A1", "1")
sheet.set_cell("A2", "1")
sheet.set_cell("A3", "1")
sheet.set_cell("A4", "1")
sheet.set_cell("A5", "1")
sheet.set_cell("B1", "12")
sheet.set_cell("B2", "12")
sheet.set_cell("B3", "12")
sheet.set_cell("B4", "12")
sheet.set_cell("B5", "12")
sheet.set_cell("C1", "=A1:A5+B1:B5")
sheet.get_cell_value("C1")
