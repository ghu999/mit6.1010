"""
6.101 Lab:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3
import os
import lab
import sys
import json
import time
import types
import random
import tempfile
import subprocess

import pytest

TEST_DIRECTORY = os.path.dirname(__file__)

MFR_NAMES = ("map", "filter", "reduce")
MFR_FILE = os.path.join(TEST_DIRECTORY, "test_files", "map_filter_reduce.scm")


class NotImplemented:
    def __eq__(self, other):
        return False


try:
    empty_rep = lab.evaluate(lab.parse(lab.tokenize("()")))
except:
    empty_rep = NotImplemented()


def list_from_ll(ll):
    if isinstance(ll, lab.Pair):
        if ll.cdr == empty_rep:
            return f'(cons {list_from_ll(ll.car)} ())'
        return f'(cons {list_from_ll(ll.car)} {list_from_ll(ll.cdr)})'
    elif ll == empty_rep:
        return '()'
    elif isinstance(ll, (float, int)):
        return ll
    else:
        return "SOMETHING"

def pingpong(*tests):
    frames = [lab.make_initial_frame() for t in tests]
    ins = []
    outs = []
    for t in tests:
        with open(os.path.join(TEST_DIRECTORY, "test_outputs", f"{t:02d}.txt")) as f:
            outs.append(iter(eval(f.read())))
        with open(os.path.join(TEST_DIRECTORY, "test_inputs", f"{t:02d}.scm")) as f:
            ins.append(iter(list(iter(f.readline, ""))))
    t = make_tester(lab.evaluate)
    while True:
        next_ins = [next(i, None) for i in ins]
        if not any(i is not None for i in next_ins):
            break
        next_outs = [next(i, None) for i in outs]
        for i, f, o in zip(next_ins, frames, next_outs):
            if i is None:
                continue
            out = t(lab.parse(lab.tokenize(i)), f)
            if out["ok"]:
                try:
                    typecheck = (int, float, lab.Pair)
                    func = list_from_ll
                except:
                    typecheck = (int, float)
                    func = lambda x: x if isinstance(x, typecheck) else "SOMETHING"
                out["output"] = func(out["output"])
            out["expression"] = i.strip()
            compare_outputs(
                out,
                o,
                msg="double-check that every call to make_initial_frame makes a completely separate object!",
            )


def make_tester(func):
    """
    Helper to wrap a function so that, when called, it produces a
    dictionary instead of its normal result.  If the function call works
    without raising an exception, then the results are included.
    Otherwise, the dictionary includes information about the exception that
    was raised.
    """

    def _tester(*args):
        try:
            return {"ok": True, "output": func(*args)}
        except lab.SchemeError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return {"ok": False, "type": exc_type.__name__, "msg": str(e)}

    return _tester


def load_test_values(n):
    """
    Helper function to load test inputs/outputs
    """
    with open(os.path.join(TEST_DIRECTORY, "test_inputs", f"{n:02d}.txt")) as f:
        inputs = eval(f.read())
    with open(os.path.join(TEST_DIRECTORY, "test_outputs", f"{n:02d}.txt")) as f:
        outputs = eval(f.read())
    return inputs, outputs


def run_continued_evaluations(ins):
    """
    Helper to evaluate a sequence of expressions in an environment.
    """
    lab.eval = None
    lab.exec = None
    frame = lab.make_initial_frame()
    outs = []
    t = make_tester(lab.evaluate)
    for i in ins:
        out = t(i, frame)
        if out["ok"]:
            try:
                typecheck = (int, float, lab.Pair)
                func = list_from_ll
            except:
                typecheck = (int, float)
                func = lambda x: x if isinstance(x, typecheck) else "SOMETHING"
            out["output"] = func(out["output"])
        outs.append(out)
    return outs


def compare_outputs(x, y, msg):
    # y is expected, x is your result
    if x["ok"]:
        assert y["ok"], (
            msg
            + f'\n\nExpected an exception ({y.get("type", None)}), but got {x.get("output", None)!r}'
        )
        if isinstance(x["output"], (int, float)):
            assert type(x["output"]) == type(y["output"]), (
                msg
                + f'\n\nOutput has incorrect type (expected {type(y.get("output", None))} but got {type(x.get("output", None))}'
            )
            assert abs(x["output"] - y["output"]) <= 1e-6, (
                msg
                + f'\n\nOutput has incorrect value (expected {y.get("output", None)!r} but got {x.get("output", None)!r})'
            )
        else:
            assert x["output"] == y["output"], (
                msg
                + f'\n\nOutput has incorrect value (expected {y.get("output", None)!r} but got {x.get("output", None)!r})'
            )
    else:
        after = '' if not x.get("msg") else f'("{x.get("msg")}")'
        assert not y["ok"], (
            msg
            + f'\n\nDid not expect an exception\nresult:   {x.get("type", None)}{after}\nexpected: {y.get("output", None)!r}'
        )
        assert x["type"] == y["type"], (
            msg
            + f'\n\nExpected {y.get("type", None)} to be raised, not {x.get("type", None)}{after}'
        )
        assert x.get("when", "eval") == y.get("when", "eval"), (
            msg
            + f'\n\nExpected error to be raised at {y.get("when", "eval")} time, not at {x.get("when", "eval")} time.'
        )


def do_continued_evaluations(n):
    """
    Test that the results from running continued evaluations in the same
    environment match the expected values.
    """
    inp, out = load_test_values(n)
    msg = message(n)
    results = run_continued_evaluations(inp)
    for x, (result, expected) in enumerate(zip(results, out)):
        m = f"\nevaluate input line {x+2}: \n\t{repr(inp[x])}"
        m += f'\nexpected:\n\t{expected.get("output") if expected.get("output") else expected.get("type")}'
        m += f'\nresult:\n\t{result.get("output") if result.get("output") else result.get("type")}'
        compare_outputs(result, expected, msg + m)


def do_raw_continued_evaluations(n, env=None):
    """
    Test that the results from running continued evaluations in the same
    environment match the expected values.
    """
    with open(os.path.join(TEST_DIRECTORY, "test_outputs", f"{n:02d}.txt")) as f:
        expected = eval(f.read())
    env = env if env is not None else lab.make_initial_frame()
    results = []
    t = make_tester(lab.evaluate)
    with open(os.path.join(TEST_DIRECTORY, "test_inputs", f"{n:02d}.scm")) as f:
        for line in iter(f.readline, ""):
            try:
                parsed = lab.parse(lab.tokenize(line.strip()))
            except lab.SchemeSyntaxError as e:
                results.append(
                    {
                        "expression": line.strip(),
                        "ok": False,
                        "type": "SchemeSyntaxError",
                        "msg": str(e),
                        "when": "parse",
                    }
                )
                continue
            out = t(parsed, env)
            if out["ok"]:
                try:
                    typecheck = (int, float, lab.Pair)
                    func = list_from_ll
                except:
                    typecheck = (int, float)
                    func = lambda x: x if isinstance(x, typecheck) else "SOMETHING"
                out["output"] = func(out["output"])
            out["expression"] = line.strip()
            results.append(out)
    for ix, (result, exp) in enumerate(zip(results, expected)):
        msg = f"for line {ix+1} in test_inputs/{n:02d}.scm:\n    {result['expression']}"
        compare_outputs(result, exp, msg=msg)


def run_test_number(n, func, fname=""):
    tester = make_tester(func)
    inp, out = load_test_values(n)
    msg = message(n)
    for x, (i, o) in enumerate(zip(inp, out)):
        m = f"\n{func.__name__ if not fname else fname} input line {x+2}: \n\t{repr(i)}"
        m += f'\nexpected:\n\t{o.get("output") if o.get("output") else o.get("type")}'
        res = tester(i)
        if o.get("output") == "SOMETHING" and res.get("output"):
            res["output"] = "SOMETHING" if not isinstance(res["output"], (int, float)) else res["output"]
        m += f'\nresult:\n\t{res.get("output") if res.get("output") else res.get("type")}'
        if not res.get("output") and res.get("msg"):
            m += f'\n\tmsg: {res.get("msg")}'
        compare_outputs(res, o, msg + m)


def message(n, include_code=False):
    sn = n if n >= 10 else "0" + str(n)
    msg = f"\nfor test_inputs/{sn}.txt"
    try:
        with open(os.path.join(TEST_DIRECTORY, "scheme_code", f"{n:02d}.scm")) as f:
            code = f.read()
        msg += f" and scheme_code/{n}.scm"
    except Exception as e:
        with open(os.path.join(TEST_DIRECTORY, "test_inputs", f"{n:02d}.txt")) as f:
            code = f.read()
    if include_code:
        msg += " that begins with\n"
        msg += code if len(code) < 100 else code[:100] + "..."
    return msg

def _test_file(fname, num, env=None):
    env = env if env is not None else lab.make_initial_frame()
    try:
        out = lab.evaluate_file(os.path.join(TEST_DIRECTORY, "test_files", fname), env)
        out = list_from_ll(out)
        out = {"ok": True, "output": out}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        out = {"ok": False, "type": exc_type.__name__, "msg": str(e)}
    with open(os.path.join(TEST_DIRECTORY, "test_outputs", f"{num}.txt")) as f:
        expected = eval(f.read())
    msg = _test_file_msg(fname, num)
    return out, expected, msg


def _test_file_msg(fname, n):
    msg = f"\nwhile running test_files/{fname} that begins with\n"
    with open(os.path.join(TEST_DIRECTORY, "test_files", fname)) as f:
        code = f.read()
    msg += code if len(code) < 80 else code[:80] + "..."
    return msg



def test_oldbehaviors():
    run_test_number(0, lab.tokenize)
    run_test_number(31, lab.tokenize)
    run_test_number(32, lab.tokenize)
    run_test_number(1, lab.parse)
    run_test_number(33, lab.parse)
    run_test_number(4, lab.evaluate)
    run_test_number(5, lab.evaluate)
    run_test_number(34, lab.evaluate)
    run_test_number(35, lab.evaluate)
    run_test_number(93, lab.evaluate)
    do_continued_evaluations(6)
    do_continued_evaluations(7)
    do_continued_evaluations(8)
    do_continued_evaluations(9)
    do_continued_evaluations(10)
    do_continued_evaluations(11)
    do_continued_evaluations(12)
    do_raw_continued_evaluations(13)
    do_raw_continued_evaluations(14)
    do_raw_continued_evaluations(15)
    do_raw_continued_evaluations(16)
    do_raw_continued_evaluations(17)
    do_raw_continued_evaluations(18)
    do_raw_continued_evaluations(19)
    do_raw_continued_evaluations(20)
    do_raw_continued_evaluations(21)
    do_raw_continued_evaluations(22)
    do_raw_continued_evaluations(23)
    do_raw_continued_evaluations(24)
    do_raw_continued_evaluations(25)
    do_raw_continued_evaluations(26)
    do_raw_continued_evaluations(27)
    do_raw_continued_evaluations(28)


def test_make_initial_frame():
    pingpong(13, 14, 15, 16, 17, 18, 19, 20)


# SYNTAX ERRORS

def test_syntax_errors_1():
    run_test_number(2, lab.parse)


def test_syntax_errors_2():
    run_test_number(3, lambda i: lab.parse(lab.tokenize(i)), "parse(tokenize(line))")



# BOOLEANS AND CONDITIONALS


def test_conditionals():
    do_raw_continued_evaluations(87)


def test_comparisons():
    do_raw_continued_evaluations(67)


# BOOLEAN COMBINATORS


def test_func():
    do_raw_continued_evaluations(88)


def test_and():
    do_raw_continued_evaluations(89)


def test_or():
    do_raw_continued_evaluations(90)


def test_not():
    do_raw_continued_evaluations(91)


def test_shortcircuit_1():
    do_raw_continued_evaluations(92)


def test_shortcircuit_2():
    do_raw_continued_evaluations(36)


def test_shortcircuit_3():
    do_raw_continued_evaluations(37)


def test_shortcircuit_4():
    do_raw_continued_evaluations(38)


def test_conditional_scoping_1():
    do_raw_continued_evaluations(39)


def test_conditional_scoping_2():
    do_raw_continued_evaluations(40)


# TESTS FOR LIST BASICS


def test_cons_lists():
    import inspect
    assert inspect.isclass(lab.Pair), f"lab should have Pair class defined"
    do_raw_continued_evaluations(41)


def test_car_cdr_1():
    do_raw_continued_evaluations(42)


def test_car_cdr_2():
    do_raw_continued_evaluations(43)


def test_islist():
    do_raw_continued_evaluations(68)


def test_length():
    do_raw_continued_evaluations(44)


def test_indexing():
    do_raw_continued_evaluations(45)


def test_append():
    do_raw_continued_evaluations(46)


def test_list_ops():
    do_raw_continued_evaluations(47)


# TESTS FOR READING CODE FROM FILES


def test_begin_1():
    do_raw_continued_evaluations(48)


def test_file_1():
    compare_outputs(*_test_file("small_test1.scm", 49))


def test_file_2():
    compare_outputs(*_test_file("small_test2.scm", 50))


def test_file_repl():
    def send_command(x):
        p.stdin.write(x.encode("utf-8") + b"\n")
        p.stdin.flush()

    def get_output():
        count = 0
        while f.peek() == b"":
            time.sleep(0.1)
            count += 1
            if count > 20:
                return ""
        return (b''.join(iter(lambda: f.read(1024), b''))).decode('utf-8')

    def try_clear_tempfile():
        try:
            os.unlink(t.name)
        except:
            pass

    t = tempfile.NamedTemporaryFile(delete=False)
    p = subprocess.Popen(
        [sys.executable, "lab.py"], cwd=TEST_DIRECTORY, stdin=subprocess.PIPE, stdout=t
    )
    try:
        os.set_blocking(t.fileno(), False)
    except:
        pass

    ra, rb, rc = [random.randint(-1000, 1000) for _ in range(3)]
    pairs = [
        (f"{ra}", lambda x: "EXCEPTION" not in x and f"out> {ra}" in x),
        (f"(+ {rb} {rc})", lambda x: "EXCEPTION" not in x and f"out> {rb+rc}" in x),
        ("fib", lambda x: "EXCEPTION" in x),
        ("(fib 20)", lambda x: "EXCEPTION" in x),
    ]


    with open(t.name, "rb") as f:
        get_output()
        for inp, out in pairs:
            send_command(inp)
            res = get_output()
            try:
                assert out(res), repr(inp) + repr(res)
                assert out(res), "unexpected output from REPL!"
            except:
                p.terminate()
                p.wait(1)
                raise
            finally:
                try_clear_tempfile()

        send_command("quit")
        try:
            p.wait(1)
        except subprocess.TimeoutExpired:
            p.terminate()
            p.wait(1)
    try_clear_tempfile()

    t = tempfile.NamedTemporaryFile(delete=False)
    p = subprocess.Popen(
        [
            sys.executable,
            "lab.py",
            os.path.join("test_files", "definitions.scm"),
            os.path.join("test_files", "small_test5.scm"),
        ],
        cwd=TEST_DIRECTORY,
        stdin=subprocess.PIPE,
        stdout=t,
    )
    try:
        os.set_blocking(t.fileno(), False)
    except:
        pass

    ra, rb, rc, rd, re, rf, rg, rh = [random.randint(-1000, 1000) for _ in range(8)]
    pairs = [
        (f"{ra}", lambda x: "EXCEPTION" not in x and f"out> {ra}" in x),
        (
            f"(+ {rb} {rc} {rd})",
            lambda x: "EXCEPTION" not in x and f"out> {rb+rc+rd}" in x,
        ),
        ("fib", lambda x: "EXCEPTION" not in x),
        ("(fib 20)", lambda x: "EXCEPTION" not in x and f"out> 6765" in x),
        (
            f"(define x (+ {re} {rf}))",
            lambda x: "EXCEPTION" not in x and f"out> {re+rf}" in x,
        ),
        (
            f"((foo {rg}) x {rh})",
            lambda x: "EXCEPTION" not in x and f"out> {rg - (re+rf) - rh}" in x,
        ),
    ]

    with open(t.name, "rb") as f:
        get_output()
        for inp, out in pairs:
            send_command(inp)
            res = get_output()
            try:
                assert out(res), repr(inp) + repr(res)
                assert out(
                    res
                ), "unexpected output from REPL!  did you implement loading files?"
            except:
                p.terminate()
                p.wait(1)
                raise
            finally:
                try_clear_tempfile()

        send_command("quit")
        try:
            p.wait(1)
        except subprocess.TimeoutExpired:
            p.terminate()
            p.wait(1)
    try_clear_tempfile()


# TESTS FOR MAP FILTER REDUCE


def test_map_filter_reduce_defined_externally_in_scheme():
    initial_frame = lab.make_initial_frame()
    for name in MFR_NAMES:
        with pytest.raises(lab.SchemeNameError):
            lab.evaluate(name, initial_frame)
    lab.evaluate_file(os.path.join(TEST_DIRECTORY, "test_files", "definitions.scm"), initial_frame)
    for name in MFR_NAMES:
        with pytest.raises(lab.SchemeNameError):
            lab.evaluate(name, initial_frame)
    lab.evaluate_file(MFR_FILE, initial_frame)
    baseline = lab.evaluate(["lambda", ["x"], "x"])
    for name in MFR_NAMES:
        res = lab.evaluate(name, initial_frame)
        assert isinstance(res, baseline.__class__)
        assert not isinstance(
            res, (types.FunctionType, types.LambdaType, types.MethodType)
        )


def test_map_1():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(MFR_FILE, initial_frame)
    do_raw_continued_evaluations(78, initial_frame)


def test_map_schemefunc():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(MFR_FILE, initial_frame)
    do_raw_continued_evaluations(79, initial_frame)


def test_filter_1():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(MFR_FILE, initial_frame)
    do_raw_continued_evaluations(80, initial_frame)


def test_filter_schemefunc():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(MFR_FILE, initial_frame)
    do_raw_continued_evaluations(81, initial_frame)


def test_reduce_1():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(MFR_FILE, initial_frame)
    do_raw_continued_evaluations(82, initial_frame)


def test_reduce_schemefunc():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(MFR_FILE, initial_frame)
    do_raw_continued_evaluations(83, initial_frame)


def test_map_filter_reduce_1():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(MFR_FILE, initial_frame)
    do_raw_continued_evaluations(84, initial_frame)


def test_file_3():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(MFR_FILE, initial_frame)
    compare_outputs(*_test_file("small_test3.scm", 51, initial_frame))


def test_file_4():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(MFR_FILE, initial_frame)
    compare_outputs(*_test_file("small_test4.scm", 85, initial_frame))


def test_file_5():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(MFR_FILE, initial_frame)
    compare_outputs(*_test_file("small_test5.scm", 86, initial_frame))


# TESTS FOR OTHER SCOPING THINGS


def test_del_1():
    do_raw_continued_evaluations(52)


def test_let_1():
    do_raw_continued_evaluations(53)


def test_let_2():
    do_raw_continued_evaluations(54)


def test_let_3():
    do_raw_continued_evaluations(55)


def test_setbang_1():
    do_raw_continued_evaluations(56)


def test_begin_2():
    do_raw_continued_evaluations(57)


def test_deep_nesting_1():
    do_raw_continued_evaluations(58)


def test_deep_nesting_2():
    do_raw_continued_evaluations(59)


def test_deep_nesting_3():
    do_raw_continued_evaluations(60)


def test_counters_oop():
    do_raw_continued_evaluations(61)


def test_fizzbuzz():
    do_raw_continued_evaluations(62)


def test_primes():
    do_raw_continued_evaluations(63)


def test_averages_oop():
    do_raw_continued_evaluations(64)


def test_nd_mines():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(
        os.path.join(TEST_DIRECTORY, "test_files", "map_filter_reduce.scm"),
        initial_frame
    )
    do_raw_continued_evaluations(65, initial_frame)


def test_sudoku_solver():
    initial_frame = lab.make_initial_frame()
    lab.evaluate_file(
        os.path.join(TEST_DIRECTORY, "test_files", "map_filter_reduce.scm"),
        initial_frame
    )
    do_raw_continued_evaluations(66, initial_frame)
