"""
6.101 Lab:
LISP Interpreter Part 1
"""

#!/usr/bin/env python3

# import doctest # optional import
# import typing  # optional import
# import pprint  # optional import

import sys

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

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
    def parse_expression(token_list):
        if token_list == []:
            return []
        if token_list[0] == '(':
            parentheses = 1
            for index, val in enumerate(token_list[1:]):
                if val == '(':
                    parentheses += 1
                elif val == ')':
                    parentheses -= 1
                if parentheses == 0:
                    break
            index += 1
            return ([parse_expression(token_list[1:index])]
                    + parse_expression(token_list[index+1:]))
        return [number_or_symbol(token_list[0])] + parse_expression(token_list[1:])
    result = parse_expression(tokens)
    return result[0]


######################
# Built-in Functions #
######################

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

scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": lambda *args: calc_mul(args),
    "/": lambda *args: calc_div(args)
}

##############
# Evaluation #
##############


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    print(tree)
    if frame is None:
        frame = make_initial_frame()
    if isinstance(tree, (int, float)):
        return tree
    elif isinstance(tree, str):
        return frame[tree]
    elif isinstance(tree, list):
        if not tree:
            return SchemeEvaluationError
        if tree[0] == 'define':
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
                print("scheme eval error")
                raise SchemeEvaluationError
        elif tree[0] == 'lambda':
            return Function(tree[2], tree[1], frame)
        else:
            function = evaluate(tree[0], frame)
            args = []
            for element in tree[1:]:
                args.append(evaluate(element, frame))
            if not callable(function):
                raise SchemeEvaluationError
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
            except:
                print("scheme name error")
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
            for var, arg in zip(self.parameters, args): mappings[var] = arg
            frame = Frame(self.frame, mappings)
            return evaluate(self.body, frame)
        else:
            raise SchemeEvaluationError
if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    import os
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl
    schemerepl.SchemeREPL(sys.modules[__name__],
                           use_frames=True, verbose=True).cmdloop()
    # print(parse(['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')']))
