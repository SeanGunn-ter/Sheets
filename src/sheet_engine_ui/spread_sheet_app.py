from textual.app import App, ComposeResult
from textual.widgets import DataTable, Input, Static
from textual.containers import Container, Vertical
from sheet_engine.SpreadSheet import Spreadsheet


class SpreadsheetApp(App):
    CSS = """
        #main {
            padding: 1;
            height: 100%;
        }

        #header {
            content-align: center middle;
            height: 3;
            border: round green;
            text-style: bold;
        }

        #table-wrapper {
            border: round green;
            height: 2fr;
            background: $panel;
            padding: 1;
        }

        #input-wrapper {
            border: round green;
            height: 0.5fr;
            background: $panel;
            padding: 1;
            layout: horizontal; 
            content-align: center middle;
        }

        #editor {
            width: 100%;
            height: 100%;
            border: round green;
            padding: 0;
        }
        #cell-header {
            content-align: center middle;
            height: 3;
            border: round green;
            text-style: bold;
        }
 
        """

    BINDINGS = [("escape", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.sheet = Spreadsheet()
        self.table = None
        self.input = None
        self.current_cell = None  # (row_key, col_key)
        self.col_count = 55
        self.row_count = 32

        self.col_key_to_name = {}
        self.row_key_to_name = {}

        self.col_name_to_key = {}
        self.row_name_to_key = {}

    def compose(self) -> ComposeResult:
        with Vertical(id="main"):
            yield Static("SpreadSheetApp", id="header")

            with Container(id="table-wrapper"):
                yield DataTable(id="table")

            with Container(id="input-wrapper"):
                yield Input(placeholder="Enter formula", id="editor")

    def on_mount(self) -> None:
        print("yoooo")
        self.table = self.query_one("#table", DataTable)
        self.input = self.query_one("#editor", Input)

        self.table.fixed_columns = 1
        self._generate_col_names(self.table)
        self._generate_rows(self.table)

    def _col_name(self, index: int) -> str:
        name = ""
        while index >= 0:
            name = chr(index % 26 + 65) + name
            index = index // 26 - 1
        return name

    def _generate_col_names(self, table):
        # col 0 -> A
        table.add_column("")
        for col in range(self.col_count):
            name = self._col_name(col)
            col_key = table.add_column(name)
            self.col_key_to_name[col_key] = name
            self.col_name_to_key[name] = col_key

    def _generate_rows(self, table):

        for row in range(self.row_count):
            blank_cells = [""] * (self.col_count + 1)
            blank_cells[0] = row + 1
            row_key = table.add_row(*blank_cells)
            self.row_key_to_name[row_key] = row + 1
            self.row_name_to_key[row + 1] = row_key

    async def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:

        self.input.focus()
        row_key, col_key = event.cell_key
        self.current_cell = (row_key, col_key)

        name = self._keys_to_cell_name(row_key, col_key)
        formula = self.sheet.get_cell_expr(name)

        self.input.value = formula if formula is not None else ""

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        input_widget = event.input
        formula = input_widget.value
        row_key = self.current_cell[0]
        col_key = self.current_cell[1]

        col_name = self.col_key_to_name[col_key]
        row_name = self.row_key_to_name[row_key]
        cell_name = col_name + str(row_name)
        self.sheet.set_cell(cell_name, formula)
        value = self.sheet.get_cell_value(cell_name)

        self.table.update_cell(row_key, col_key, value, update_width=True)
        self._update_dependents(cell_name)

    def _update_dependents(self, cell_name):
        rev_deps = self.sheet.rev_deps.get(cell_name, [])
        for dep in rev_deps:
            value = self.sheet.get_cell_value(dep)
            row_key, col_key = self._cell_name_to_keys(dep)
            self.table.update_cell(row_key, col_key, value, update_width=True)
            self._update_dependents(dep)

    def _cell_name_to_keys(self, cell_name: str):
        import re

        match = re.match(r"([A-Z]+)(\d+)", cell_name)
        if not match:
            raise ValueError(f"Invalid cell name: {cell_name}")
        col_name, row_num = match.groups()
        col_key = self.col_name_to_key.get(col_name)
        row_key = self.row_name_to_key.get(int(row_num))
        return (row_key, col_key)

    def _keys_to_cell_name(self, row_key, col_key):
        col_name = self.col_key_to_name.get(col_key)
        row_num = self.row_key_to_name.get(row_key)
        return f"{col_name}{row_num}"


def main():
    SpreadsheetApp().run()


if __name__ == "__main__":
    main()
