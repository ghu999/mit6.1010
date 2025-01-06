"""
6.101 Lab:
Symbolic Algebra
"""

#!/usr/bin/env python3
import os
import lab
import ast
import pytest
import random
import builtins

ttype = type
iisinstance = isinstance

TEST_DIRECTORY = os.path.dirname(__file__)


def expression_rep(x):
    """
    Recursively converts an Expr object x into a new object consisting of
    only built-in types that can be checked for equality against expected
    results without relying on any lab.py functionality
    """
    if iisinstance(x, lab.BinOp):
        if x.__class__.__name__ in {"Add", "Mul"}:  # commutative operations
            op_rep = frozenset
        elif x.__class__.__name__ in {"Sub", "Div"}:
            op_rep = tuple
        else:
            raise NotImplementedError(f"No support for {type(x)}")
        return (x.__class__.__name__, op_rep(expression_rep(i) for i in (x.left, x.right)))
    elif iisinstance(x, lab.Num):
        return ("Num", x.n)
    elif iisinstance(x, lab.Var):
        return ("Var", x.name)
    else:
        raise NotImplementedError(f"No support for {type(x)}")


def expression_hash(x):
    return hash(expression_rep(x))


class DisallowedFunctionException(Exception):
    pass


def _disallowed(*args, **kwargs):
    raise DisallowedFunctionException("using disallowed type or isinstance function")


def _make_test_display_00(test=0):
    def the_test(*args):
        exp = lab.Add(lab.Num(0), lab.Var("x"))
        expected = ("Add(Num(0), Var('x'))", "0 + x")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Add(lab.Var("x"), lab.Num(0))
        expected = ("Add(Var('x'), Num(0))", "x + 0")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Mul(lab.Num(1), lab.Var("x"))
        expected = ("Mul(Num(1), Var('x'))", "1 * x")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Mul(lab.Var("x"), lab.Num(1))
        expected = ("Mul(Var('x'), Num(1))", "x * 1")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Sub(lab.Var("x"), lab.Num(0))
        expected = ("Sub(Var('x'), Num(0))", "x - 0")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Div(lab.Var("x"), lab.Num(1))
        expected = ("Div(Var('x'), Num(1))", "x / 1")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Div(lab.Num(0), lab.Var("x"))
        expected = ("Div(Num(0), Var('x'))", "0 / x")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Add(lab.Num(20), lab.Num(30))
        expected = ("Add(Num(20), Num(30))", "20 + 30")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Sub(lab.Num(50), lab.Num(80))
        expected = ("Sub(Num(50), Num(80))", "50 - 80")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Div(lab.Num(40), lab.Num(20))
        expected = ("Div(Num(40), Num(20))", "40 / 20")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Mul(lab.Num(101), lab.Num(121))
        expected = ("Mul(Num(101), Num(121))", "101 * 121")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

    return the_test


def _make_test_display_01(test=0):
    def the_test(*args):
        exp = lab.Add(lab.Num(0), lab.Mul(lab.Var("y"), lab.Num(2)))
        expected = ("Add(Num(0), Mul(Var('y'), Num(2)))", "0 + y * 2")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Add(lab.Mul(lab.Var("z"), lab.Num(3)), lab.Num(0))
        expected = ("Add(Mul(Var('z'), Num(3)), Num(0))", "z * 3 + 0")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Mul(lab.Num(1), lab.Add(lab.Var("A"), lab.Var("x")))
        expected = ("Mul(Num(1), Add(Var('A'), Var('x')))", "1 * (A + x)")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Mul(lab.Sub(lab.Var("x"), lab.Var("A")), lab.Num(1))
        expected = ("Mul(Sub(Var('x'), Var('A')), Num(1))", "(x - A) * 1")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Sub(lab.Mul(lab.Var("x"), lab.Num(3)), lab.Num(0))
        expected = ("Sub(Mul(Var('x'), Num(3)), Num(0))", "x * 3 - 0")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Div(lab.Mul(lab.Num(7), lab.Var("A")), lab.Num(1))
        expected = ("Div(Mul(Num(7), Var('A')), Num(1))", "7 * A / 1")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Div(lab.Num(0), lab.Add(lab.Var("A"), lab.Num(3)))
        expected = ("Div(Num(0), Add(Var('A'), Num(3)))", "0 / (A + 3)")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Mul(lab.Add(lab.Num(0), lab.Var("x")), lab.Var("z"))
        expected = ("Mul(Add(Num(0), Var('x')), Var('z'))", "(0 + x) * z")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Sub(lab.Add(lab.Var("x"), lab.Num(0)), lab.Var("A"))
        expected = ("Sub(Add(Var('x'), Num(0)), Var('A'))", "x + 0 - A")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Add(lab.Mul(lab.Num(1), lab.Var("x")), lab.Var("y"))
        expected = ("Add(Mul(Num(1), Var('x')), Var('y'))", "1 * x + y")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Add(lab.Var("z"), lab.Mul(lab.Var("x"), lab.Num(1)))
        expected = ("Add(Var('z'), Mul(Var('x'), Num(1)))", "z + x * 1")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Sub(lab.Var("A"), lab.Sub(lab.Var("x"), lab.Num(0)))
        expected = ("Sub(Var('A'), Sub(Var('x'), Num(0)))", "A - (x - 0)")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Div(lab.Var("y"), lab.Div(lab.Var("x"), lab.Num(1)))
        expected = ("Div(Var('y'), Div(Var('x'), Num(1)))", "y / (x / 1)")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Mul(lab.Var("z"), lab.Div(lab.Num(0), lab.Var("x")))
        expected = ("Mul(Var('z'), Div(Num(0), Var('x')))", "z * 0 / x")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Add(lab.Mul(lab.Num(0), lab.Var("y")), lab.Var("x"))
        expected = ("Add(Mul(Num(0), Var('y')), Var('x'))", "0 * y + x")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Add(lab.Var("x"), lab.Sub(lab.Num(2), lab.Num(2)))
        expected = ("Add(Var('x'), Sub(Num(2), Num(2)))", "x + 2 - 2")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Mul(lab.Div(lab.Num(2), lab.Num(2)), lab.Var("x"))
        expected = ("Mul(Div(Num(2), Num(2)), Var('x'))", "2 / 2 * x")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Mul(lab.Var("x"), lab.Sub(lab.Num(3), lab.Num(2)))
        expected = ("Mul(Var('x'), Sub(Num(3), Num(2)))", "x * (3 - 2)")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Sub(lab.Var("x"), lab.Mul(lab.Num(0), lab.Var("z")))
        expected = ("Sub(Var('x'), Mul(Num(0), Var('z')))", "x - 0 * z")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Div(lab.Var("x"), lab.Num(1))
        expected = ("Div(Var('x'), Num(1))", "x / 1")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Div(lab.Add(lab.Num(0), lab.Num(0)), lab.Var("x"))
        expected = ("Div(Add(Num(0), Num(0)), Var('x'))", "(0 + 0) / x")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = read_expected("52_in.pyobj")
        expected = read_expected("52_out.pyobj")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Sub(lab.Add(lab.Num(70), lab.Num(50)), lab.Num(80))
        expected = ("Sub(Add(Num(70), Num(50)), Num(80))", "70 + 50 - 80")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = lab.Sub(lab.Num(80), lab.Div(lab.Num(40), lab.Num(20)))
        expected = ("Sub(Num(80), Div(Num(40), Num(20)))", "80 - 40 / 20")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = read_expected("55_in.pyobj")
        expected = read_expected("55_out.pyobj")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

    return the_test


def _make_test_display_02(test=0):
    def the_test(*args):
        exp = read_expected("56_in.pyobj")
        expected = read_expected("56_out.pyobj")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = read_expected("57_in.pyobj")
        expected = read_expected("57_out.pyobj")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = read_expected("58_in.pyobj")
        expected = read_expected("58_out.pyobj")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = read_expected("59_in.pyobj")
        expected = read_expected("59_out.pyobj")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = read_expected("60_in.pyobj")
        expected = read_expected("60_out.pyobj")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = read_expected("61_in.pyobj")
        expected = read_expected("61_out.pyobj")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = read_expected("62_in.pyobj")
        expected = read_expected("62_out.pyobj")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

        exp = read_expected("63_in.pyobj")
        expected = read_expected("63_out.pyobj")
        if test == 0:
            assert expression_rep(safe_eval(repr(exp))) == expression_rep(
                safe_eval(expected[0])
            ), "Incorrect repr result!"
        else:
            assert str(exp) == expected[1], "Incorrect str result!"

    return the_test


# RUN DISPLAY TESTS


def test_display_repr_behavior():
    _make_test_display_00(0)()
    _make_test_display_01(0)()
    _make_test_display_02(0)()

test_display_str_behavior_00 = _make_test_display_00(1)
test_display_str_behavior_01 = _make_test_display_01(1)
test_display_str_behavior_02 = _make_test_display_02(1)


def test_combinations_00():
    result = 0 + lab.Var("x")
    expected = ("Add", frozenset({("Var", "x"), ("Num", 0)}))
    assert expression_rep(result) == expected

    result = lab.Var("x") + 0
    expected = ("Add", frozenset({("Var", "x"), ("Num", 0)}))
    assert expression_rep(result) == expected

    result = 0 + (lab.Var("y") * 2)
    expected = (
        "Add",
        frozenset({("Mul", frozenset({("Num", 2), ("Var", "y")})), ("Num", 0)}),
    )
    assert expression_rep(result) == expected

    result = ("z" * lab.Num(3)) + 0
    expected = (
        "Add",
        frozenset({("Mul", frozenset({("Num", 3), ("Var", "z")})), ("Num", 0)}),
    )
    assert expression_rep(result) == expected

    result = (lab.Num(0) + "x") * "z"
    expected = (
        "Mul",
        frozenset({("Var", "z"), ("Add", frozenset({("Var", "x"), ("Num", 0)}))}),
    )
    assert expression_rep(result) == expected

    result = (0 * lab.Var("y")) + lab.Var("x")
    expected = (
        "Add",
        frozenset({("Mul", frozenset({("Var", "y"), ("Num", 0)})), ("Var", "x")}),
    )
    assert expression_rep(result) == expected

    result = "x" + (lab.Num(2) - 2)
    expected = ("Add", frozenset({("Var", "x"), ("Sub", (("Num", 2), ("Num", 2)))}))
    assert expression_rep(result) == expected

    result = 20 + lab.Num(101) * (1 * lab.Var("z"))
    expected = (
        "Add",
        frozenset(
            {
                (
                    "Mul",
                    frozenset(
                        {("Mul", frozenset({("Num", 1), ("Var", "z")})), ("Num", 101)}
                    ),
                ),
                ("Num", 20),
            }
        ),
    )
    assert expression_rep(result) == expected

    result = "x" - lab.Num(101)
    expected = ("Sub", (("Var", "x"), ("Num", 101)))
    assert expression_rep(result) == expected

    result = "x" / lab.Num(101)
    expected = ("Div", (("Var", "x"), ("Num", 101)))
    assert expression_rep(result) == expected

    result = lab.Num(101) / "x"
    expected = ("Div", (("Num", 101), ("Var", "x")))
    assert expression_rep(result) == expected

    result = lab.Num(101) - "x"
    expected = ("Sub", (("Num", 101), ("Var", "x")))
    assert expression_rep(result) == expected


def make_eval_check(inp, vars, expected):
    def check():
        result = inp.eval(vars)
        assert abs(result / expected - 1) <= 1e-4

    return check


def test_eval_00():
    inp = lab.Add(lab.Num(0), lab.Var("x"))
    vars = {"x": 877}
    expected = 877
    make_eval_check(inp, vars, expected)()

    inp = lab.Mul(lab.Num(1), lab.Var("x"))
    vars = {"x": -365}
    expected = -365
    make_eval_check(inp, vars, expected)()

    inp = lab.Mul(lab.Var("y"), lab.Num(2))
    vars = {"y": -296}
    expected = -592
    make_eval_check(inp, vars, expected)()

    inp = lab.Add(lab.Mul(lab.Var("z"), lab.Num(3)), lab.Num(0))
    vars = {"z": 400}
    expected = 1200
    make_eval_check(inp, vars, expected)()

    inp = lab.Div(lab.Mul(lab.Num(7), lab.Var("A")), lab.Num(9))
    vars = {"A": 610}
    expected = 474.44444444444446
    make_eval_check(inp, vars, expected)()

    inp = lab.Add(lab.Var("z"), lab.Add(lab.Var("x"), lab.Num(1)))
    vars = {"z": -596, "x": -554}
    expected = -1149
    make_eval_check(inp, vars, expected)()
    with pytest.raises(NameError):
        inp.eval({"z": 500})

    inp = lab.Sub(lab.Var("A"), lab.Add(lab.Var("x"), lab.Var("A")))
    vars = {"A": 539, "x": -789}
    expected = 789
    make_eval_check(inp, vars, expected)()
    with pytest.raises(NameError):
        inp.eval({"A": 5})

    inp = lab.Div(lab.Var("y"), lab.Div(lab.Var("x"), lab.Var("z")))
    vars = {"z": 693, "y": -71, "x": -391}
    expected = 125.83887468030692
    make_eval_check(inp, vars, expected)()
    with pytest.raises(NameError):
        inp.eval(
            {
                "z": 693,
                "y": -71,
            }
        )

    inp = lab.Mul(lab.Mul(lab.Var("x"), lab.Var("y")), lab.Var("z"))
    vars = {"z": 816, "y": 732, "x": -225}
    expected = -134395200
    make_eval_check(inp, vars, expected)()
    with pytest.raises(NameError):
        inp.eval(
            {
                "z": 693,
                "y": -71,
            }
        )

    inp = read_expected("156_in.pyobj")
    vars = {"z": 984, "A": -801, "x": -880, "y": 96}
    expected = -1815480
    make_eval_check(inp, vars, expected)()
    with pytest.raises(NameError):
        inp.eval(
            {
                "z": 693,
                "y": -71,
            }
        )


def test_eval_01():
    inp = lab.Sub(lab.Var("k"), lab.Num(5))
    vars = {"k": 583}
    expected = 578
    make_eval_check(inp, vars, expected)()
    assert expression_rep(inp) == expression_rep(
        lab.Sub(lab.Var("k"), lab.Num(5))
    ), f"Input to eval should not be mutated!"

    inp = read_expected("158_in.pyobj")
    inp2 = read_expected("158_in.pyobj")
    vars = {
        "Q": -960,
        "T": 696,
        "Y": 895,
        "H": -395,
        "y": -752,
        "F": 973,
        "l": 581,
        "X": 853,
        "G": -370,
        "q": -403,
        "V": 211,
        "v": 203,
        "n": -859,
        "t": -794,
        "o": -710,
        "N": 640,
        "L": 958,
        "g": 46,
        "J": 796,
        "f": 127,
        "w": 706,
        "S": 351,
        "B": 454,
        "O": 45,
        "D": 848,
        "u": -729,
        "E": 394,
        "C": -230,
        "p": -497,
        "a": 494,
        "Z": 890,
        "j": 601,
        "K": -273,
        "I": -432,
        "e": 809,
        "s": 453,
        "i": -90,
        "R": 421,
        "U": 720,
        "P": -248,
        "m": 56,
        "k": -20,
    }
    expected = -24447405.102586962
    make_eval_check(inp, vars, expected)()
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("159_in.pyobj")
    inp2 = read_expected("159_in.pyobj")
    vars = {
        "P": 865,
        "r": -635,
        "g": -328,
        "L": -77,
        "b": 272,
        "B": -892,
        "h": 569,
        "H": -411,
        "D": 606,
        "y": -891,
        "W": 278,
        "u": 411,
        "p": 769,
        "C": -557,
        "z": -478,
        "j": 547,
        "A": -273,
        "K": -671,
        "I": 156,
        "M": -942,
        "s": -991,
        "V": 33,
        "U": 951,
        "m": 695,
        "t": 337,
        "o": -27,
        "N": -392,
        "k": 865,
    }
    expected = 3.079655919243488e-13
    make_eval_check(inp, vars, expected)()
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("160_in.pyobj")
    inp2 = read_expected("160_in.pyobj")
    vars = {
        "r": -831,
        "Q": -249,
        "T": -12,
        "H": -582,
        "l": -408,
        "G": -796,
        "V": -412,
        "n": -166,
        "N": -116,
        "g": 30,
        "S": -281,
        "B": 969,
        "x": -690,
        "O": 17,
        "W": -977,
        "u": 844,
        "C": -425,
        "Z": -304,
        "j": -617,
        "A": 757,
        "I": 742,
        "i": -660,
        "U": -916,
        "R": -46,
        "b": -809,
        "y": -861,
        "F": 316,
        "z": 295,
        "q": 201,
        "M": 368,
        "v": 952,
        "t": -597,
        "d": 874,
        "o": 745,
        "L": 812,
        "J": -55,
        "w": 153,
        "h": -249,
        "D": -310,
        "p": 289,
        "s": -535,
        "P": 629,
        "m": 705,
        "k": -130,
    }
    expected = -3036189255.554901
    make_eval_check(inp, vars, expected)()
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("161_in.pyobj")
    inp2 = read_expected("161_in.pyobj")
    vars = {
        "g": 867,
        "L": 954,
        "w": 686,
        "f": -711,
        "o": -227,
        "h": -634,
        "O": 799,
        "y": 594,
        "D": -115,
        "u": 394,
        "a": 960,
        "X": -987,
        "v": -163,
        "U": -887,
        "t": 527,
        "d": 657,
        "N": 400,
    }
    expected = 4741737.246211018
    make_eval_check(inp, vars, expected)()
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("162_in.pyobj")
    inp2 = read_expected("162_in.pyobj")
    vars = {
        "J": -150,
        "X": -302,
        "w": 332,
        "s": 927,
        "v": -687,
        "B": -740,
        "E": 671,
        "k": -539,
    }
    expected = 347.0000000000164
    make_eval_check(inp, vars, expected)()
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("163_in.pyobj")
    inp2 = read_expected("163_in.pyobj")
    vars = {
        "P": -228,
        "Q": -6,
        "g": 896,
        "d": -417,
        "T": -870,
        "b": -138,
        "S": 835,
        "x": -405,
        "h": 719,
        "H": 766,
        "y": -982,
        "D": 766,
        "E": -376,
        "C": 832,
        "l": -559,
        "X": 323,
        "K": -630,
        "q": 548,
        "I": -809,
        "V": -849,
        "M": 122,
        "c": 173,
        "o": -875,
        "m": -395,
    }
    expected = -4004783415.5644646
    make_eval_check(inp, vars, expected)()
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"

    inp = read_expected("164_in.pyobj")
    inp2 = read_expected("164_in.pyobj")
    vars = {
        "L": -750,
        "d": -449,
        "T": -230,
        "f": -843,
        "o": 280,
        "O": -840,
        "h": -729,
        "y": -658,
        "D": -724,
        "W": 502,
        "E": 578,
        "F": -198,
        "Z": -23,
        "e": 360,
        "v": 666,
        "U": 927,
        "m": 230,
        "t": -944,
        "P": 742,
        "N": 446,
    }
    expected = 1475.6592465238434
    make_eval_check(inp, vars, expected)()
    assert expression_rep(inp) == expression_rep(
        inp2
    ), f"Input to eval should not be mutated!"


def test_eq_00():
    expressions = [
        (lab.Num(0.0), lab.Num(0), True),
        (lab.Num(1.0), lab.Num(1), True),
        (lab.Var("x"), lab.Var("x"), True),
        (lab.Var("z"), lab.Var("y"), False),
        (lab.Num(4), lab.Num(4), True),
        (lab.Num(-5), lab.Num(-5.0), True),
        (lab.Num(2.999), lab.Num(3), False),
        (lab.Add(lab.Num(4), lab.Var("x")), lab.Add(lab.Num(4), lab.Var("x")), True),
        (lab.Add(lab.Var("y"), lab.Num(5)), lab.Add(lab.Num(5), lab.Var("y")), False),
        (
            lab.Add(lab.Num(10), lab.Add(lab.Num(4), lab.Var("x"))),
            lab.Add(lab.Num(10), lab.Add(lab.Num(4), lab.Var("x"))),
            True,
        ),
        (lab.Sub(lab.Num(4.0), lab.Var("x")), lab.Sub(lab.Num(4), lab.Var("x")), True),
        (lab.Sub(lab.Var("y"), lab.Num(5)), lab.Sub(lab.Num(5), lab.Var("y")), False),
        (
            lab.Sub(lab.Num(10), lab.Add(lab.Num(4.0), lab.Var("x"))),
            lab.Sub(lab.Num(10), lab.Add(lab.Num(4), lab.Var("x"))),
            True,
        ),
        (lab.Div(lab.Num(4), lab.Var("x")), lab.Div(lab.Num(4), lab.Var("x")), True),
        (lab.Div(lab.Var("y"), lab.Num(5)), lab.Div(lab.Num(5), lab.Var("y")), False),
        (
            lab.Div(lab.Num(10.9), lab.Add(lab.Num(4), lab.Var("x"))),
            lab.Div(lab.Num(10.9), lab.Add(lab.Num(4), lab.Var("x"))),
            True,
        ),
        (
            lab.Mul(lab.Num(-4), lab.Var("x")),
            lab.Mul(lab.Num(-4.0), lab.Var("x")),
            True,
        ),
        (lab.Mul(lab.Var("y"), lab.Num(5)), lab.Mul(lab.Num(5), lab.Var("y")), False),
        (
            lab.Mul(lab.Num(10), lab.Add(lab.Num(4), lab.Var("x"))),
            lab.Mul(lab.Num(10), lab.Add(lab.Num(4), lab.Var("x"))),
            True,
        ),
        (read_expected("86_in.pyobj"), read_expected("86_in.pyobj"), True),
        (read_expected("76_in.pyobj"), read_expected("75_in.pyobj"), False),
    ]

    for e1, e2, exp in expressions:
        assert (
            e1 == e2
        ) is exp, f"{repr(e1)} == {repr(e2)} should be {exp} but got {not exp}!"

    for i, express1 in enumerate(expressions):
        for express2 in expressions[i + 1 :]:
            assert (
                express1[0] != express2[0]
            ), f"{repr(express1[0])} != {repr(express2[0])} but got True!"
            assert (
                express1[1] != express2[1]
            ), f"{repr(express1[1])} != {repr(express2[1])} but got True!"


def test_deriv_00():
    exp = lab.Add(lab.Var("x"), lab.Num(5))

    result = lab.Add(exp, exp).deriv("x")
    expected = lab.Add(lab.Add(lab.Num(1), lab.Num(0)), lab.Add(lab.Num(1), lab.Num(0)))
    assert expression_rep(result) == expression_rep(expected), f"{result} != {expected}"

    result = lab.Sub(exp, exp).deriv("x")
    expected = lab.Sub(lab.Add(lab.Num(1), lab.Num(0)), lab.Add(lab.Num(1), lab.Num(0)))
    assert expression_rep(result) == expression_rep(expected), f"{result} != {expected}"

    result = lab.Div(lab.Var("x"), lab.Num(5)).deriv("x")
    expected = lab.Div(
        lab.Sub(lab.Mul(lab.Num(5), lab.Num(1)), lab.Mul(lab.Var("x"), lab.Num(0))),
        lab.Mul(lab.Num(5), lab.Num(5)),
    )
    assert expression_rep(result) == expression_rep(expected), f"{result} != {expected}"

    result = lab.Mul(lab.Var("x"), lab.Num(5)).deriv("x")
    expected = lab.Add(
        lab.Mul(lab.Num(5), lab.Num(1)), lab.Mul(lab.Var("x"), lab.Num(0))
    )
    assert expression_rep(result) == expression_rep(expected), f"{result} != {expected}"

    exp = lab.Add(lab.Var("x"), lab.Mul(lab.Var("x"), lab.Var("x")))
    exp2 = lab.Add(lab.Var("x"), lab.Mul(lab.Var("x"), lab.Var("x")))
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("74_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"

    exp = read_expected("75_in.pyobj")
    exp2 = read_expected("75_in.pyobj")
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("75_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"

    exp = read_expected("76_in.pyobj")
    exp2 = read_expected("76_in.pyobj")
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("76_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"

    exp = lab.Mul(lab.Mul(lab.Var("x"), lab.Var("x")), lab.Var("x"))
    exp2 = lab.Mul(lab.Mul(lab.Var("x"), lab.Var("x")), lab.Var("x"))
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("77_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"

    exp = lab.Mul(lab.Mul(lab.Var("x"), lab.Var("y")), lab.Var("z"))
    exp2 = lab.Mul(lab.Mul(lab.Var("x"), lab.Var("y")), lab.Var("z"))
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("78_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"

    exp = read_expected("79_in.pyobj")
    exp2 = read_expected("79_in.pyobj")
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("79_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"

    exp = lab.Add(lab.Add(lab.Num(0), lab.Var("y")), lab.Var("x"))
    exp2 = lab.Add(lab.Add(lab.Num(0), lab.Var("y")), lab.Var("x"))
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("80_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"

    exp = lab.Num(0)
    exp2 = lab.Num(0)
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = [lab.Num(0), lab.Num(0), lab.Num(0), lab.Num(0), lab.Num(0)]
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"

    exp = lab.Sub(lab.Var("x"), lab.Mul(lab.Var("x"), lab.Var("x")))
    exp2 = lab.Sub(lab.Var("x"), lab.Mul(lab.Var("x"), lab.Var("x")))
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("82_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"

    exp = lab.Sub(lab.Mul(lab.Var("x"), lab.Var("x")), lab.Var("x"))
    exp2 = lab.Sub(lab.Mul(lab.Var("x"), lab.Var("x")), lab.Var("x"))
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("83_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)

    exp = lab.Div(lab.Var("y"), lab.Mul(lab.Var("x"), lab.Var("x")))
    exp2 = lab.Div(lab.Var("y"), lab.Mul(lab.Var("x"), lab.Var("x")))
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("84_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"

    exp = lab.Div(lab.Mul(lab.Var("x"), lab.Var("x")), lab.Var("y"))
    exp2 = lab.Div(lab.Mul(lab.Var("x"), lab.Var("x")), lab.Var("y"))
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("85_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"

    exp = read_expected("86_in.pyobj")
    exp2 = read_expected("86_in.pyobj")
    out = (
        exp.deriv("x"),
        exp.deriv("y"),
        exp.deriv("x").deriv("x").deriv("x"),
        exp.deriv("y").deriv("x"),
        exp.deriv("z"),
    )
    expected = read_expected("86_out.pyobj")
    for i, j in zip(out, expected):
        assert expression_rep(i) == expression_rep(j)
    assert expression_rep(exp) == expression_rep(exp2), f"Input to deriv should not be mutated!"


def test_simplify_00():
    result = lab.Add(lab.Num(0), lab.Var("x"))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Add(lab.Var("x"), lab.Num(0))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Mul(lab.Num(1), lab.Var("x"))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Mul(lab.Var("x"), lab.Num(1))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Sub(lab.Var("x"), lab.Num(0))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Div(lab.Var("x"), lab.Num(1))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Div(lab.Num(0), lab.Var("x"))
    expected = lab.Num(0)
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Add(lab.Num(20), lab.Num(30))
    expected = lab.Num(50)
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Sub(lab.Num(50), lab.Num(80))
    expected = lab.Num(-30)
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Div(lab.Num(40), lab.Num(20))
    expected = lab.Num(2.0)
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Mul(lab.Num(101), lab.Num(121))
    expected = lab.Num(12221)
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Div(lab.Num(2), lab.Num(2))
    expected = lab.Num(1.0)
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Div(lab.Var("x"), lab.Var("x"))
    expected = lab.Div(lab.Var("x"), lab.Var("x"))
    assert expression_rep(result.simplify()) == expression_rep(
        expected
    ), f"Make sure to not oversimplify!"

    result = lab.Div(lab.Var("x"), lab.Num(0))
    expected = lab.Div(lab.Var("x"), lab.Num(0))
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Sub(lab.Var("x"), lab.Var("x"))
    expected = lab.Sub(lab.Var("x"), lab.Var("x"))
    assert expression_rep(result.simplify()) == expression_rep(
        expected
    ), f"Make sure to not oversimplify!"

    result = lab.Sub(lab.Num(0), lab.Var("x"))
    expected = lab.Sub(lab.Num(0), lab.Var("x"))
    assert expression_rep(result.simplify()) == expression_rep(expected)

    result = lab.Add(lab.Var("x"), lab.Var("x"))
    expected = lab.Add(lab.Var("x"), lab.Var("x"))
    assert expression_rep(result.simplify()) == expression_rep(
        expected
    ), f"Make sure to not oversimplify!"

    result = lab.Mul(lab.Var("x"), lab.Var("x"))
    expected = lab.Mul(lab.Var("x"), lab.Var("x"))
    assert expression_rep(result.simplify()) == expression_rep(
        expected
    ), f"Make sure to not oversimplify!"


def test_simplify_01():
    result_copy = lab.Add(lab.Num(0), lab.Mul(lab.Var("y"), lab.Num(2)))
    result = lab.Add(lab.Num(0), lab.Mul(lab.Var("y"), lab.Num(2)))
    expected = lab.Mul(lab.Var("y"), lab.Num(2))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Add(lab.Mul(lab.Var("z"), lab.Num(3)), lab.Num(0))
    result = lab.Add(lab.Mul(lab.Var("z"), lab.Num(3)), lab.Num(0))
    expected = lab.Mul(lab.Var("z"), lab.Num(3))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Mul(lab.Num(1), lab.Add(lab.Var("A"), lab.Var("x")))
    result = lab.Mul(lab.Num(1), lab.Add(lab.Var("A"), lab.Var("x")))
    expected = lab.Add(lab.Var("A"), lab.Var("x"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Mul(lab.Sub(lab.Var("x"), lab.Var("A")), lab.Num(1))
    result = lab.Mul(lab.Sub(lab.Var("x"), lab.Var("A")), lab.Num(1))
    expected = lab.Sub(lab.Var("x"), lab.Var("A"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Sub(lab.Mul(lab.Var("x"), lab.Num(3)), lab.Num(0))
    result = lab.Sub(lab.Mul(lab.Var("x"), lab.Num(3)), lab.Num(0))
    expected = lab.Mul(lab.Var("x"), lab.Num(3))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Div(lab.Mul(lab.Num(7), lab.Var("A")), lab.Num(1))
    result = lab.Div(lab.Mul(lab.Num(7), lab.Var("A")), lab.Num(1))
    expected = lab.Mul(lab.Num(7), lab.Var("A"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Div(lab.Num(0), lab.Add(lab.Var("A"), lab.Num(3)))
    result = lab.Div(lab.Num(0), lab.Add(lab.Var("A"), lab.Num(3)))
    expected = lab.Num(0)
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Mul(lab.Add(lab.Num(0), lab.Var("x")), lab.Var("z"))
    result = lab.Mul(lab.Add(lab.Num(0), lab.Var("x")), lab.Var("z"))
    expected = lab.Mul(lab.Var("x"), lab.Var("z"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Sub(lab.Add(lab.Var("x"), lab.Num(0)), lab.Var("A"))
    result = lab.Sub(lab.Add(lab.Var("x"), lab.Num(0)), lab.Var("A"))
    expected = lab.Sub(lab.Var("x"), lab.Var("A"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Add(lab.Mul(lab.Num(1), lab.Var("x")), lab.Var("y"))
    result = lab.Add(lab.Mul(lab.Num(1), lab.Var("x")), lab.Var("y"))
    expected = lab.Add(lab.Var("x"), lab.Var("y"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Add(lab.Var("z"), lab.Mul(lab.Var("x"), lab.Num(1)))
    result = lab.Add(lab.Var("z"), lab.Mul(lab.Var("x"), lab.Num(1)))
    expected = lab.Add(lab.Var("z"), lab.Var("x"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Sub(lab.Var("A"), lab.Sub(lab.Var("x"), lab.Num(0)))
    result = lab.Sub(lab.Var("A"), lab.Sub(lab.Var("x"), lab.Num(0)))
    expected = lab.Sub(lab.Var("A"), lab.Var("x"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Div(lab.Var("y"), lab.Div(lab.Var("x"), lab.Num(1)))
    result = lab.Div(lab.Var("y"), lab.Div(lab.Var("x"), lab.Num(1)))
    expected = lab.Div(lab.Var("y"), lab.Var("x"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Mul(lab.Var("z"), lab.Div(lab.Num(0), lab.Var("x")))
    result = lab.Mul(lab.Var("z"), lab.Div(lab.Num(0), lab.Var("x")))
    expected = lab.Num(0)
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Add(lab.Mul(lab.Num(0), lab.Var("y")), lab.Var("x"))
    result = lab.Add(lab.Mul(lab.Num(0), lab.Var("y")), lab.Var("x"))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Add(lab.Var("x"), lab.Sub(lab.Num(2), lab.Num(2)))
    result = lab.Add(lab.Var("x"), lab.Sub(lab.Num(2), lab.Num(2)))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Mul(lab.Div(lab.Num(2), lab.Num(2)), lab.Var("x"))
    result = lab.Mul(lab.Div(lab.Num(2), lab.Num(2)), lab.Var("x"))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Mul(lab.Var("x"), lab.Sub(lab.Num(3), lab.Num(2)))
    result = lab.Mul(lab.Var("x"), lab.Sub(lab.Num(3), lab.Num(2)))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Sub(lab.Var("x"), lab.Mul(lab.Num(0), lab.Var("z")))
    result = lab.Sub(lab.Var("x"), lab.Mul(lab.Num(0), lab.Var("z")))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Div(lab.Var("x"), lab.Num(1))
    result = lab.Div(lab.Var("x"), lab.Num(1))
    expected = lab.Var("x")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Div(lab.Add(lab.Num(0), lab.Num(0)), lab.Var("x"))
    result = lab.Div(lab.Add(lab.Num(0), lab.Num(0)), lab.Var("x"))
    expected = lab.Num(0)
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = read_expected("123_in.pyobj")
    result = read_expected("123_in.pyobj")
    expected = lab.Num(800)
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Sub(lab.Add(lab.Num(70), lab.Num(50)), lab.Num(80))
    result = lab.Sub(lab.Add(lab.Num(70), lab.Num(50)), lab.Num(80))
    expected = lab.Num(40)
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Sub(lab.Num(80), lab.Div(lab.Num(40), lab.Num(20)))
    result = lab.Sub(lab.Num(80), lab.Div(lab.Num(40), lab.Num(20)))
    expected = lab.Num(78.0)
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = read_expected("126_in.pyobj")
    result = read_expected("126_in.pyobj")
    expected = lab.Add(lab.Num(20), lab.Mul(lab.Num(101), lab.Var("z")))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"


def test_simplify_02():
    result_copy = lab.Sub(lab.Num(1), lab.Var("L"))
    result = lab.Sub(lab.Num(1), lab.Var("L"))
    expected = lab.Sub(lab.Num(1), lab.Var("L"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Add(lab.Var("b"), lab.Num(1))
    result = lab.Add(lab.Var("b"), lab.Num(1))
    expected = lab.Add(lab.Var("b"), lab.Num(1))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = read_expected("129_in.pyobj")
    result = read_expected("129_in.pyobj")
    expected = read_expected("129_out.pyobj")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = read_expected("130_in.pyobj")
    result = read_expected("130_in.pyobj")
    expected = read_expected("130_out.pyobj")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = read_expected("131_in.pyobj")
    result = read_expected("131_in.pyobj")
    expected = lab.Sub(lab.Div(lab.Num(-1), lab.Var("I")), lab.Num(-1))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = read_expected("132_in.pyobj")
    result = read_expected("132_in.pyobj")
    expected = read_expected("132_out.pyobj")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Div(lab.Var("M"), lab.Var("D"))
    result = lab.Div(lab.Var("M"), lab.Var("D"))
    expected = lab.Div(lab.Var("M"), lab.Var("D"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = read_expected("134_in.pyobj")
    result = read_expected("134_in.pyobj")
    expected = read_expected("134_out.pyobj")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = read_expected("135_in.pyobj")
    result = read_expected("135_in.pyobj")
    expected = read_expected("135_out.pyobj")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = read_expected("136_in.pyobj")
    result = read_expected("136_in.pyobj")
    expected = read_expected("136_out.pyobj")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = read_expected("137_in.pyobj")
    result = read_expected("137_in.pyobj")
    expected = read_expected("137_out.pyobj")
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

    result_copy = lab.Div(lab.Add(lab.Num(1), lab.Var("Q")), lab.Var("k"))
    result = lab.Div(lab.Add(lab.Num(1), lab.Var("Q")), lab.Var("k"))
    expected = lab.Div(lab.Add(lab.Num(1), lab.Var("Q")), lab.Var("k"))
    assert expression_rep(result.simplify()) == expression_rep(expected)
    assert expression_rep(result) == expression_rep(
        result_copy
    ), f"Input to simplify should not be mutated!"

def test_make_expression_00():
    result = lab.make_expression("x")
    expected = lab.Var("x")
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("20")
    expected = lab.Num(20)
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("6.1010")
    expected = lab.Num(6.1010)
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("-4.9")
    expected = lab.Num(-4.9)
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("(0 + x)")
    expected = lab.Add(lab.Num(0), lab.Var("x"))
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("(-101 * x)")
    expected = lab.Mul(lab.Num(-101), lab.Var("x"))
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("(x + (-.5 / x))")
    expected = lab.Add(lab.Var("x"), lab.Div(lab.Num(-0.5), lab.Var("x")))
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("(y * -2)")
    expected = lab.Mul(lab.Var("y"), lab.Num(-2))
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("((z * 3) + 0)")
    expected = lab.Add(lab.Mul(lab.Var("z"), lab.Num(3)), lab.Num(0))
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("((7 * A) / 9)")
    expected = lab.Div(lab.Mul(lab.Num(7), lab.Var("A")), lab.Num(9))
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("(z + (x + 1))")
    expected = lab.Add(lab.Var("z"), lab.Add(lab.Var("x"), lab.Num(1)))
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("(A - (x + A))")
    expected = lab.Sub(lab.Var("A"), lab.Add(lab.Var("x"), lab.Var("A")))
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("(y / (x / z))")
    expected = lab.Div(lab.Var("y"), lab.Div(lab.Var("x"), lab.Var("z")))
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("((x * y) * z)")
    expected = lab.Mul(lab.Mul(lab.Var("x"), lab.Var("y")), lab.Var("z"))
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression("((x + A) * (y + z))")
    expected = read_expected("187_out.pyobj")
    assert expression_rep(result) == expression_rep(expected)


def test_make_expression_01():
    result = lab.make_expression(read_expected("188_in.pyobj"))
    expected = read_expected("188_out.pyobj")
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression(read_expected("189_in.pyobj"))
    expected = read_expected("189_out.pyobj")
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression(read_expected("190_in.pyobj"))
    expected = read_expected("190_out.pyobj")
    assert expression_rep(result) == expression_rep(expected)

    result = lab.make_expression(read_expected("191_in.pyobj"))
    expected = read_expected("191_out.pyobj")
    assert expression_rep(result) == expression_rep(expected)

def test_custom_make_exp():
    result = lab.make_expression("((x + 2) + y)")
    expected = lab.Add(lab.Add(lab.Var('x'), lab.Num(2)), lab.Var('y'))
    assert result == expected

    result = lab.make_expression("((x * y) / z)")
    expected = lab.Div(lab.Mul(lab.Var('x'), lab.Var('y')), lab.Var('z'))
    assert result == expected

# TESTING UTILS DO NOT MODIFY!
from collections import OrderedDict

_unprep_funcs = {
    "OrderedDict": OrderedDict,
    "frozenset": frozenset,
    "set": set,
}
for i in ("Add", "Sub", "Mul", "Div", "Var", "Num"):
    _a = getattr(lab, i, None)
    if _a is not None:
        _unprep_funcs[i] = _a


def safe_eval(node_or_string):
    if isinstance(node_or_string, str):
        node_or_string = ast.parse(node_or_string, mode="eval")
    if isinstance(node_or_string, ast.Expression):
        node_or_string = node_or_string.body

    def _convert(node):
        if isinstance(node, (ast.Constant)):
            return node.value
        elif isinstance(node, ast.Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, ast.List):
            return list(map(_convert, node.elts))
        elif isinstance(node, ast.Set):
            return set(map(_convert, node.elts))
        elif isinstance(node, ast.Dict):
            return dict(
                (_convert(k), _convert(v)) for k, v in zip(node.keys, node.values)
            )
        elif isinstance(node, ast.Constant):
            return node.value
        elif (
            isinstance(node, ast.UnaryOp)
            and isinstance(node.op, (ast.UAdd, ast.USub))
            and isinstance(node.operand, (ast.Constant, ast.UnaryOp, ast.BinOp))
        ):
            operand = _convert(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            else:
                return -operand
        elif (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, (ast.Add, ast.Sub))
            and isinstance(node.right, (ast.Constant, ast.UnaryOp, ast.BinOp))
            and isinstance(node.left, (ast.Constant, ast.UnaryOp, ast.BinOp))
        ):
            left = _convert(node.left)
            right = _convert(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            else:
                return left - right
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in _unprep_funcs
        ):
            return _unprep_funcs[node.func.id](*(_convert(i) for i in node.args))
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in _unprep_funcs
        ):
            return _unprep_funcs[node.func.attr](*(_convert(i) for i in node.args))
        raise ValueError("malformed node or string: " + repr(node))

    return _convert(node_or_string)


# read in expected result
def read_expected(fname):
    with open(os.path.sep.join([TEST_DIRECTORY, "testing_data", fname]), "r") as f:
        return safe_eval(f.read())
