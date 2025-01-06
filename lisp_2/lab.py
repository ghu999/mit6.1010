"""
6.101 Lab:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3
import sys
sys.setrecursionlimit(20_000)


#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass

# KEEP THE ABOVE LINES INTACT, BUT REPLACE THIS COMMENT WITH YOUR lab.py FROM
# THE PREVIOUS LAB, WHICH SHOULD BE THE STARTING POINT FOR THIS LAB.

############################
# Tokenization and Parsing #
############################
def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    if value == '#t': return True
    if value == '#f': return False
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    result = ""
    comment = False
    for i in source:
        if i in "()" and not comment:
            result += " " + i + " "
        elif i == ";":
            comment = True
        elif i == "\n" and comment:
            comment = False
        elif not comment:
            result += i
    return result.split()

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    stack = []
    started = False
    for i in tokens:
        if i == '(':
            started = True
            stack.append(i)
        elif i == ')':
            if not stack:
                raise SchemeSyntaxError
            stack.pop()
        elif i == 'define':
            if not started:
                raise SchemeSyntaxError
        else:
            if not stack and started:
                raise SchemeSyntaxError
    if stack:
        raise SchemeSyntaxError
    def parse_expression(token_list):
        if token_list == []:
            return []
        if token_list[0] == '(':
            parentheses = 1
            for indx, val in enumerate(token_list[1:]):
                if val == '(':
                    parentheses += 1
                elif val == ')':
                    parentheses -= 1
                if parentheses == 0:
                    break
            indx += 1
            return ([parse_expression(token_list[1:indx])]
                    + parse_expression(token_list[indx+1:]))
        return [number_or_symbol(token_list[0])] + parse_expression(token_list[1:])
    result = parse_expression(tokens)
    return result[0]

######################
# Built-in Functions #
######################
class EmptyList:
    def __repr__(self):
        return "empty list"
    def __eq__(self, other):
        return isinstance(other, (EmptyList, list))
    def __str__(self):
        return "()"

empty = EmptyList()

def calc_sub(*args):
    if len(args) == 1:
        return -args[0]

    first_num, *rest_nums = args
    return first_num - scheme_builtins['+'](*rest_nums)

def calc_mul(args):
    product = 1
    for i in args:
        product *= i
    return product

def calc_div(args):
    if len(args) == 0:
        raise SchemeEvaluationError
    if len(args) == 1:
        return 1 / args[0]
    return args[0] / calc_mul(args[1:])

def calc_greater_than(args):
    for i in range(1, len(args)):
        if args[i] >= args[i-1]:
            return False
    return True

def calc_greater_than_equal(args):
    for i in range(1, len(args)):
        if args[i] > args[i-1]:
            return False
    return True

def calc_less_than(args):
    for i in range(1, len(args)):
        if args[i] <= args[i-1]:
            return False
    return True

def calc_less_than_equal(args):
    for i in range(1, len(args)):
        if args[i] < args[i-1]:
            return False
    return True

def calc_not(*args):
    if len(args) != 1:
        raise SchemeEvaluationError
    return not args[0]

def create_list(*args):
    if len(args) != 2:
        raise SchemeEvaluationError
    return Pair(args[0], args[1])

def equals(args):
    first = args[0]
    for arg in args:
        if arg != first:
            return False
    return True

def find_car(*args):
    if len(args) != 1 or not isinstance(args[0], Pair):
        raise SchemeEvaluationError
    return args[0].car

def find_cdr(*args):
    if len(args) != 1 or not isinstance(args[0], Pair):
        raise SchemeEvaluationError
    return args[0].cdr

def make_list(*args):
    result = empty
    for i in reversed(args):
        result = Pair(i, result)
    return result

def is_list(*args):
    if len(args) != 1:
        raise SchemeEvaluationError
    if args[0] == empty:
        return True
    if isinstance(args[0], Pair):
        return is_list(args[0].cdr)

def calc_len(args):
    """
    Calculate length of list
    """
    if len(args) != 1:
        raise SchemeEvaluationError
    if not is_list(args[0]):
        raise SchemeEvaluationError
    print(len(args))
    length = 0
    arg = args[0]
    while arg != empty:
        length += 1
        arg = arg.cdr
    return length

def index(args):
    """
    Find element at index of list
    """
    if len(args) != 2:
        raise SchemeEvaluationError
    if (not is_list(args[0]) and not isinstance(args[0], Pair)
        or not isinstance(args[1], int)):
        raise SchemeEvaluationError
    cell, ind = args[0], args[1]
    print(cell, ind, type(cell))
    start = 0
    while cell != empty and start < ind:
        cell = cell.cdr
        print(cell)
        start += 1
    if cell == empty or isinstance(cell, int):
        raise SchemeEvaluationError
    return cell.car

def append(args):
    """
    Append argument to list
    """
    for arg in args:
        if not is_list(arg): raise SchemeEvaluationError
    if len(args) == 0:
        return empty
    def shallow_copy(inp):
        if inp == empty:
            return empty
        return Pair(inp.car, shallow_copy(inp.cdr))
    result = shallow_copy(args[0])
    curr = result
    for arg in args[1:]:
        while curr != empty and curr.cdr != empty:
            curr = curr.cdr
        if curr == empty:
            result = shallow_copy(arg)
        else:
            curr.cdr = shallow_copy(arg)
    return result

scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": lambda *args: calc_mul(args),
    "/": lambda *args: calc_div(args),
    "equal?": lambda *args: equals(args),
    ">": lambda *args: calc_greater_than(args),
    ">=": lambda *args: calc_greater_than_equal(args),
    "<=": lambda *args: calc_less_than_equal(args),
    "<": lambda *args: calc_less_than(args),
    "not": calc_not,
    "cons": create_list,
    "car": find_car,
    "cdr": find_cdr,
    "list": make_list,
    "list?": is_list,
    "length": lambda *args: calc_len(args),
    "list-ref": lambda *args: index(args),
    "append": lambda *args: append(args)
}



##############
# Evaluation #
##############

keywords = ["and", "or", "begin", "del", "let", "set!", "lambda", "if", "define"]

def eval_func(tree, frame):
    """
    Finds the correct function to evaluate based on keyword
    """
    keyword = tree[0]
    funcs = {
        "and": eval_and,
        "or": eval_or,
        "begin": eval_begin,
        "del": eval_del,
        "let": eval_let,
        "set!": eval_set,
        "lambda": eval_lambda,
        "if": eval_if,
        "define": eval_define
    }
    func = funcs.get(keyword)
    if func:
        return func(tree, frame)
    return None

def eval_and(tree, frame):
    for expression in tree[1:]:
        if not evaluate(expression, frame):
            return False
    return True

def eval_or(tree, frame):
    for expression in tree[1:]:
        if evaluate(expression, frame):
            return True
    return False

def evaluate_file(name, frame=None):
    with open(name, "r", encoding="utf-8") as file:
        line = file.read()
    parsed_expression = parse(tokenize(line))
    return evaluate(parsed_expression, frame)

def eval_begin(tree, frame):
    for exp in tree[1:-1]:
        evaluate(exp, frame)
    return evaluate(tree[-1], frame)

def eval_del(tree, frame):
    return frame.delete(tree[1])

def eval_let(tree, frame):
    new_frame = Frame(frame)
    for var, val in tree[1]:
        new_frame.mappings[var] = evaluate(val, new_frame)
    return evaluate(tree[2], new_frame)

def eval_set(tree, frame):
    return frame.setbang(tree[1], evaluate(tree[2], frame))

def eval_lambda(tree, frame):
    if not isinstance(tree[1], list):
        raise SchemeEvaluationError
    return Function(tree[2], tree[1], frame)

def eval_if(tree, frame):
    if len(tree) != 4:
        raise SchemeEvaluationError("Incorrect if amount of arguments")
    result = evaluate(tree[1], frame)
    if result:
        return evaluate(tree[2], frame)
    else:
        return evaluate(tree[3], frame)

def eval_define(tree, frame):
    """
    Evaluate define keyword
    """
    if len(tree) == 3:
        if not isinstance(tree[1], list):
            var, exp = tree[1], tree[2]
            result = evaluate(exp, frame)
            frame.mappings[var] = result
            return result
        else:
            parameters, body = tree[1], tree[2]
            func = Function(body, parameters[1:], frame)
            frame.mappings[parameters[0]] = func
            return func
    else:
        raise SchemeEvaluationError(str(len(tree)) + " amount of arguments defined")


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    #print(tree, type(tree))
    if frame is None:
        frame = make_initial_frame()
    if isinstance(tree, (int, float, bool)):
        return tree
    if not tree:
        return empty
    if isinstance(tree, str):
        return frame[tree]
    if isinstance(tree, list):
        if not tree:
            return empty
        if isinstance(tree[0], str) and tree[0] in keywords:
            return eval_func(tree, frame)
        else:
            function = evaluate(tree[0], frame)
            args = []
            for element in tree[1:]:
                args.append(evaluate(element, frame))
            if not callable(function):
                raise SchemeEvaluationError("not callable")
            if isinstance(function, Function):
                return function(args)
            elif callable(function):
                return function(*args)


def make_initial_frame():
    """
    Create initial frame
    """
    original = Frame(None, scheme_builtins)
    return Frame(original)

class Frame:
    """
    Frame class
    """
    def __init__(self, parent=None, mappings=None):
        if mappings is None:
            mappings = {}
        self.parent = parent
        self.mappings = mappings
    def __contains__(self, var_name):
        if var_name in self.mappings:
            return True
        else:
            if self.parent is not None and var_name in self.parent:
                return True
        return False

    def __getitem__(self, var_name):
        try:
            return self.mappings[var_name]
        except KeyError:
            try:
                return self.parent[var_name]
            except Exception as exc:
                raise SchemeNameError("Not in frame", var_name) from exc

    def delete(self, var_name):
        try:
            val = self.mappings[var_name]
            del self.mappings[var_name]
            return val
        except Exception as exc:
            raise SchemeNameError from exc

    def setbang(self, var_name, val):
        if var_name in self.mappings:
            self.mappings[var_name] = val
            return val
        elif self.parent:
            self.parent.setbang(var_name, val)
            return val
        else:
            raise SchemeNameError

    def __iter__(self):
        yield from self.mappings.keys()

class Function:
    """
    Define a function in Scheme
    """
    def __init__(self, body, parameters=None, frame=None):
        self.parameters = parameters
        self.body = body
        self.frame = frame

        if frame is None:
            frame = make_initial_frame()

    def __call__(self, args):
        if len(self.parameters) == len(args):
            mappings = {}
            for var, arg in zip(self.parameters, args):
                mappings[var] = arg
            frame = Frame(self.frame, mappings)
            return evaluate(self.body, frame)
        else:
            raise SchemeEvaluationError
class Pair:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr
    def __repr__(self):
        return str(self.car) + " " + str(self.cdr) + ")"
    def __str__(self):
        return "(" + str(self.car) + " " + str(self.cdr) + ")"

if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl
    global_frame = make_initial_frame()
    for fil in sys.argv[1:]:
        evaluate_file(fil, global_frame)
    schemerepl.SchemeREPL(sys.modules[__name__], use_frames=True,
                          verbose=False, repl_frame=global_frame).cmdloop()
