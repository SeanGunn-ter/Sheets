from textual.app import App, ComposeResult
from textual.widgets import DataTable, Input
from textual.containers import Container
from sheet_engine.SpreadSheet import Spreadsheet


class SpreadsheetApp(App):
    show_log = True

    BINDINGS = [("escape", "quit", "Quit")]

    CSS = """
    Input {
        border: none;
    }
    """

    def __init__(self):
        super().__init__()
        self.sheet = Spreadsheet()
        self.current_cell = None

    def compose(self) -> ComposeResult:
        yield DataTable(id="table")
        with Container(id="editor-container"):
            yield Input(placeholder="Enter formula", id="editor")

    def on_mount(self) -> None:
        table = self.query_one("#table", DataTable)

        table.fixed_rows = 1
        table.fixed_columns = 1

        self._generate_col_names(table)
        self._generate_row_names(table)

    def _col_name(self, index: int) -> str:
        name = ""
        while index >= 0:
            name = chr(index % 26 + 65) + name
            index = index // 26 - 1
        return name

    def _generate_col_names(self, table, cols=43):
        # col 0 -> A
        table.add_column("")
        for col in range(cols):
            table.add_column(self._col_name(col))

    def _generate_row_names(self, table, cols=43, rows=43):

        for row in range(rows):
            blank_cells = []
            for i in range(cols + 1):
                blank_cells.append("")
            blank_cells[0] = row + 1
            table.add_row(*blank_cells)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        input_widget = event.input
        formula = input_widget.value

        if self.current_cell:
            row, col = self.current_cell
            # dont allow editng first col
            if col != 0:
                cell_name = self._col_name(col - 1) + str(row + 1)  # skip labels
                rev_deps = self.sheet.rev_deps.get(cell_name, 0)
                self.sheet.set_cell(cell_name, formula)

                # update cell
                value = self.sheet.get_cell_value(cell_name)
                table = self.query_one("#table", DataTable)
                table.update_cell_at((row, col), value, update_width=True)

                # updates deps
                if rev_deps:
                    for dep in rev_deps:
                        value = self.sheet.get_cell_value(dep)
                        cords = self.cell_name_to_cords(dep)
                        table.update_cell_at(cords, value, update_width=True)

            # reset input
            input_widget.value = ""

    async def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        self.current_cell = (event.coordinate.row, event.coordinate.column)
        editor = self.query_one("#editor", Input)
        editor.focus()

    def cell_name_to_cords(self, name: str) -> tuple:
        col_part = ""
        row_part = ""
        for char in name:
            if char.isdigit():
                row_part += char
            else:
                col_part += char

        # A -> 0, B -> 1
        col_index = 0
        for c in col_part:
            col_index = col_index * 26 + (ord(c) - ord("A") + 1)
            # second loop, *26 , so AA -> first loop, col=1, second loop: 1*26+1 =27

        row_index = int(row_part) - 1

        return (row_index, col_index)


if __name__ == "__main__":
    SpreadsheetApp().run()
