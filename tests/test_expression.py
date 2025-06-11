import pytest
from sheet_engine.SpreadSheet import Expression
from sheet_engine.expr_types import (
    Expr,
    LiteralInt,
    CellId,
    Plus,
    Minus,
    Multiply,
    Divide,
    Sum,
)


def test_simple_expr():
    expr = Expression("=A1+5")

    assert isinstance(expr.tree, Sum)

    assert isinstance(expr.tree.expr_lst[0], CellId)
    assert expr.tree.expr_lst[0].name == "A1"

    assert isinstance(expr.tree.expr_lst[1], LiteralInt)
    assert expr.tree.expr_lst[1].value == 5


def test_sum():
    expr = Expression("=A1+C2+3")
    tree = expr.tree
    assert isinstance(tree, Sum)
    assert len(tree.expr_lst) == 3
    assert isinstance(tree.expr_lst[0], CellId)
    assert tree.expr_lst[0].name == "A1"
    assert isinstance(tree.expr_lst[1], CellId)
    assert tree.expr_lst[1].name == "C2"
    assert isinstance(tree.expr_lst[2], LiteralInt)
    assert tree.expr_lst[2].value == 3


# python -m pytest tests/test_expression.py
