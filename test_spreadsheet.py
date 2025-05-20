import pytest
from SpreadSheet import Spreadsheet


def test_constant_value():
    sheet = Spreadsheet((10, 10))
    sheet.set_cell("A1", "10")
    sheet.set_cell("B1", "11")
    sheet.set_cell("C1", "12")

    assert sheet.get_cell_value("A1") == 10
    assert sheet.get_cell_value("B1") == 11
    assert sheet.get_cell_value("C1") == 12


def test_default_value():
    sheet = Spreadsheet((702, 10))
    sheet.set_sheet("1")
    assert sheet.get_cell_value("A1") == 1
    assert sheet.get_cell_value("GE3") == 1
    assert sheet.get_cell_value("AC10") == 1
    assert sheet.get_cell_value("ZZ10") == 1


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


def test_circular_reference_detection():
    sheet = Spreadsheet((10, 10))
    sheet.set_cell("A1", "=B1")
    sheet.set_cell("B1", "=A1")
    with pytest.raises(ValueError, match="Circular dependency detected"):
        sheet.get_cell_value("B1")

    sheet2 = Spreadsheet((10, 10))
    sheet2.set_cell("A1", "5")
    sheet2.set_cell("B1", "=A1+5")
    sheet2.set_cell("A1", "=B1")
    with pytest.raises(ValueError, match="Circular dependency detected"):
        sheet.get_cell_value("B1")


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


def test_column_op():
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

    assert sheet.get_cell_value("C1") == 13
    assert sheet.get_cell_value("C2") == 13
    assert sheet.get_cell_value("C3") == 13
    assert sheet.get_cell_value("C4") == 13
    assert sheet.get_cell_value("C5") == 13
    assert sheet.deps["C1"] == {"C2", "C3", "C4", "C5"}
    assert sheet.deps["A1"] == {"C1"}
    assert sheet.deps["A2"] == {"C2"}

    sheet.set_cell("A1", "2")
    assert sheet.get_cell_value("C1") == 14
    assert sheet.get_cell_value("C2") == 13
