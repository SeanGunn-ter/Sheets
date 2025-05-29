import pytest
from sheet_engine.SpreadSheet import Spreadsheet


def test_constant_value():
    sheet = Spreadsheet((10, 10))
    sheet.set_cell("A1", "10")
    sheet.set_cell("B1", "11")
    sheet.set_cell("C1", "12")

    assert sheet.get_cell_value("A1") == 10
    assert sheet.get_cell_value("B1") == 11
    assert sheet.get_cell_value("C1") == 12


def test_simple_formula():
    sheet = Spreadsheet((10, 10))
    sheet.set_cell("A1", "10")
    sheet.set_cell("B1", "=A1+5")
    sheet.set_cell("C1", "15")

    assert sheet.get_cell_value("B1") == 15
    sheet.set_cell("A1", "0")
    assert sheet.get_cell_value("B1") == 5
    sheet.set_cell("B1", "=C1+C1")
    assert sheet.get_cell_value("B1") == 30
    sheet.set_cell("A1", "5")
    sheet.set_cell("D1", "15")

    sheet.set_cell("B1", "=C1+50+A1+D1")
    assert sheet.get_cell_value("B1") == 85


def test_pemdas():
    sheet = Spreadsheet((10, 10))
    sheet.set_cell("A1", "10")
    sheet.set_cell("B1", "5")
    sheet.set_cell("C1", "=(3*3)+A1+A1+B1")
    sheet.set_cell("D1", "=5+2*3+2^2")
    sheet.set_cell("E1", "=3+4*2/(1-5)")

    assert sheet.get_cell_value("C1") == 34
    assert sheet.get_cell_value("D1") == 15
    assert sheet.get_cell_value("E1") == 1


# figure out
def test_circular_reference_detection():
    sheet = Spreadsheet((10, 10))
    sheet.set_cell("A1", "=B1")
    with pytest.raises(ValueError, match="Circular dependency detected"):
        sheet.set_cell("B1", "=A1")

    sheet2 = Spreadsheet((10, 10))
    sheet2.set_cell("A1", "5")
    sheet2.set_cell("B1", "=A1+5")
    with pytest.raises(ValueError, match="Circular dependency detected"):
        sheet2.set_cell("A1", "=B1")


def test_intensive_dependencies():
    sheet = Spreadsheet((10, 10))

    sheet.set_cell("A1", "1")
    sheet.set_cell("A2", "=A1 + 1")
    sheet.set_cell("A3", "=A2 + 1")
    sheet.set_cell("A4", "=A3 + 1")
    sheet.set_cell("A5", "=A4 + 1")
    sheet.set_cell("B1", "=A5 + A3")

    assert sheet.get_cell_value("A5") == 5
    assert sheet.get_cell_value("B1") == 8

    sheet.set_cell("A1", "5")
    assert sheet.get_cell_value("A5") == 9
    assert sheet.get_cell_value("B1") == 16

    sheet2 = Spreadsheet((10, 10))

    sheet2.set_cell("A1", "1")
    sheet2.set_cell("A2", "=A1 + 1")
    sheet2.set_cell("A3", "=A2 + 1")
    sheet2.set_cell("A4", "=A3 + 1")
    sheet2.set_cell("A5", "=A4 + 1")
    sheet2.set_cell("B1", "=A5 + A3")

    assert sheet2.get_cell_value("A5") == 5
    assert sheet2.get_cell_value("B1") == 8

    sheet2.set_cell("A3", "=A1")
    assert sheet2.get_cell_value("A5") == 3
    assert sheet2.get_cell_value("B1") == 4

    sheet3 = Spreadsheet((10, 10))

    sheet3.set_cell("A1", "1")
    sheet3.set_cell("A2", "=A1 + 1")
    sheet3.set_cell("A3", "=A2 + 1")
    sheet3.set_cell("A4", "=A3 + 1")
    sheet3.set_cell("A5", "=A4 + 1")
    sheet3.set_cell("B1", "6")
    sheet3.set_cell("C1", "=B1")

    sheet3.set_cell("E1", "=C1 + A3")

    assert sheet3.get_cell_value("E1") == 9
    sheet3.set_cell("A2", "=10")
    assert sheet3.get_cell_value("E1") == 17


def test_diamond_dependency():
    sheet = Spreadsheet((100, 100))
    sheet.set_cell("A1", "1")
    sheet.set_cell("B1", "=A1 + 1")
    sheet.set_cell("C1", "=A1 + 2")
    sheet.set_cell("D1", "=B1+C1")

    assert sheet.get_cell_value("D1") == 5
    assert sheet.evaluate_count == 4


def test_larger_diamond_dependency():
    sheet = Spreadsheet((100, 100))
    width = 5
    sheet.set_cell("A1", "1")

    for i in range(1, width + 1):
        sheet.set_cell(f"B{i}", f"=A1+{i}")

    for i in range(1, width + 1):
        sheet.set_cell(f"C{i}", f"=B{i}+{i}")

    sum_expr = "=" + "+".join([f"C{i}" for i in range(1, width + 1)])
    sheet.set_cell("D1", sum_expr)

    assert sheet.get_cell_value("D1") == 35
    # this is working as intended, A1: evaluated once, B1-B5: evaluated 5 times, C1-C5: evaluated 5 times, D1:evaluted once
    assert sheet.evaluate_count == 12

    sheet = Spreadsheet((200, 200))
    sheet.evaluate_count = 0
    width = 100

    sheet.set_cell("A1", "1")

    for i in range(1, width + 1):
        sheet.set_cell(f"B{i}", f"=A1+{i}")

    sum_expr = "=" + "+".join([f"B{i}" for i in range(1, width + 1)])
    sheet.set_cell("C1", sum_expr)
    assert sheet.get_cell_value("C1") == 5150
    assert sheet.evaluate_count == 1 + 1 + 100


# python -m pytest tests/test_spreadsheet.py
