import pytest
from sheet_engine.SpreadSheet import Expression
from sheet_engine.formula import (
    Formula,
    LiteralInt,
    CellId,
    Plus,
    Minus,
    Multiply,
    Divide,
    Sum,
)


def test_basic_operators():
    expr = Expression("=10 - 2")
    assert repr(expr.tree) == "Minus(LiteralInt(10), LiteralInt(2))"

    expr = Expression("=3*4")
    assert repr(expr.tree) == "Multiply(LiteralInt(3), LiteralInt(4))"

    expr = Expression("=8/2")
    assert repr(expr.tree) == "Divide(LiteralInt(8), LiteralInt(2))"


def test_parentheses():
    expr = Expression("=(A1 + 2) * 3")
    assert repr(expr.tree) == "Multiply(Sum(CellId(A1), LiteralInt(2)), LiteralInt(3))"

    expr = Expression("=3 * (4 + 5)")
    assert (
        repr(expr.tree) == "Multiply(LiteralInt(3), Sum(LiteralInt(4), LiteralInt(5)))"
    )


def test_simple_expr():
    expr = Expression("=A1+5")
    assert repr(expr.tree) == "Sum(CellId(A1), LiteralInt(5))"

    expr = Expression("=A1+5*5")
    assert repr(expr.tree) == "Sum(CellId(A1), Multiply(LiteralInt(5), LiteralInt(5)))"

    expr = Expression("=A1+C2+3")
    assert repr(expr.tree) == "Sum(CellId(A1), CellId(C2), LiteralInt(3))"


def test_sum_func():
    expr = Expression("=Sum(A1, 5, C3)")
    assert repr(expr.tree) == "Sum(CellId(A1), LiteralInt(5), CellId(C3))"


def test_concat_func():
    expr = Expression("=Concat(A1, B2, 3)")
    assert repr(expr.tree) == "Concat(CellId(A1), CellId(B2), LiteralInt(3))"


def test_power_func():
    expr = Expression("=A1^2")
    assert repr(expr.tree) == "Power(CellId(A1), LiteralInt(2))"


def test_max_min_funcs():
    expr = Expression("=Max(1, A1, 7)")
    assert repr(expr.tree) == "Max(LiteralInt(1), CellId(A1), LiteralInt(7))"

    expr = Expression("=Min(A1, B2)")
    assert repr(expr.tree) == "Min(CellId(A1), CellId(B2))"


def test_nested_funcs():
    expr = Expression("=Sum(If(A1, 1, 0), Max(3, 4))")
    assert repr(expr.tree) == (
        "Sum(If(CellId(A1), LiteralInt(1), LiteralInt(0)), Max(LiteralInt(3), LiteralInt(4)))"
    )


# python -m pytest tests/test_expression.py
