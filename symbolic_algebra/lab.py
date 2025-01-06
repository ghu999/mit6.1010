"""
6.101 Lab:
Symbolic Algebra
"""

# import doctest # optional import
# import typing # optional import
# import pprint # optional import
# import string # optional import

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Expr:
    """
    Expression that is the superclass of all other classes
    """
    def __add__(self, other):
        return Add(self, other)
    def __radd__(self, other):
        return Add(other, self)
    def __sub__(self, other):
        return Sub(self, other)
    def __rsub__(self, other):
        return Sub(other, self)
    def __mul__(self, other):
        return Mul(self, other)
    def __rmul__(self, other):
        return Mul(other, self)
    def __truediv__(self, other):
        return Div(self, other)
    def __rtruediv__(self, other):
        return Div(other, self)
    def simplify(self):
        """
        Simpify the expression
        """
        return self

class Var(Expr):
    """
    Variable with a letter name
    """
    def __init__(self, name):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = name
        self.level = 3
    def __str__(self):
        return self.name
    def __repr__(self):
        return f"Var('{self.name}')"
    def eval(self, mapping):
        """
        Evaluate the expression by returning the variable number
        """
        if self.name in mapping.keys():
            return mapping[self.name]
        raise NameError
    def __eq__(self, other):
        if repr(self) == repr(other):
            return True
        return False
    def deriv(self, var):
        """
        Take the derivative by its derivative rule
        """
        if self.name == var:
            return Num(1)
        return Num(0)
    def simplify(self):
        """
        Simpify the expression
        """
        return self

class Num(Expr):
    """
    Number object with a number value
    """
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n
        self.level = 3

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"
    def eval(self, _):
        """
        Evaluate the expression by returning the number
        """
        return self.n
    def __eq__(self, other):
        if isinstance(self, type(other)):
            return float(str(self)) == float(str(other))
        return False
    def deriv(self, _):
        """
        Take the derivative by its derivative rule
        """
        return Num(0)
    def simplify(self):
        """
        Simpify the expression
        """
        return self

class BinOp(Expr):
    """
    Binary operation between two objects (num and/or var)
    """
    def __init__(self, left, right):
        if isinstance(left, int):
            left = Num(left)
        elif isinstance(left, str):
            left = Var(left)
        if isinstance(right, int):
            right = Num(right)
        elif isinstance(right, str):
            right = Var(right)
        self.left = left
        self.right = right
    def __repr__(self):
        return (self.__class__.__name__ + "(" +
                repr(self.left) + ", " + repr(self.right) + ")")
    def __str__(self):
        left = str(self.left)
        right = str(self.right)
        #if self.level
        if self.level == 2:
            if self.left.level < self.level:
                left = "(" + left + ")"
            if self.right.level < self.level:
                right = "(" + right + ")"
        if self.level == 2 and self.special and self.right.level == self.level:
            right = "(" + right + ")"
        if self.level == 1 and self.special and self.right.level == self.level:
            right = "(" + right + ")"
        return left + " " + self.operation + " " + right
    def __eq__(self, other):
        if isinstance(self, type(other)):
            return self.left == other.left and self.right == other.right
        return False

class Add(BinOp):
    """
    Add operation
    """
    special = False
    def __init__(self, left, right):
        BinOp.__init__(self, left, right)
        self.operation = "+"
        self.level = 1
    def eval(self, mapping):
        """
        Evaluate the expression
        """
        return self.left.eval(mapping) + self.right.eval(mapping)
    def deriv(self, var):
        """
        Take the derivative by its derivative rule
        """
        return Add(self.left.deriv(var), self.right.deriv(var))
    def simplify(self):
        """
        Simpify the expression
        """
        result = Add(self.left.simplify(), self.right.simplify())
        if isinstance(result.left, Num) and isinstance(result.right, Num):
            return Num(result.left.n + result.right.n)
        if isinstance(result.left, Num):
            if result.left.n == 0:
                return result.right
        if isinstance(result.right, Num):
            if result.right.n == 0:
                return result.left
        return result

class Sub(BinOp):
    """
    Subtraction operation
    """
    special = True
    def __init__(self, left, right):
        BinOp.__init__(self, left, right)
        self.operation = "-"
        self.level = 1
    def eval(self, mapping):
        """
        Evaluate the expression
        """
        return self.left.eval(mapping) - self.right.eval(mapping)
    def deriv(self, var):
        """
        Take the derivative by its derivative rule
        """
        return Sub(self.left.deriv(var), self.right.deriv(var))
    def simplify(self):
        """
        Simpify the expression
        """
        result = Sub(self.left.simplify(), self.right.simplify())
        if isinstance(result.left, Num) and isinstance(result.right, Num):
            return Num(result.left.n - result.right.n)
        if isinstance(result.right, Num):
            if result.right.n == 0:
                return result.left
        return result
class Mul(BinOp):
    """
    Multiplication operation
    """
    special = False
    def __init__(self, left, right):
        BinOp.__init__(self, left, right)
        self.operation = "*"
        self.level = 2
    def eval(self, mapping):
        """
        Evaluate the expression
        """
        return self.left.eval(mapping) * self.right.eval(mapping)
    def deriv(self, var):
        """
        Take the derivative by its derivative rule
        """
        return Add(Mul(self.left.deriv(var), self.right),
                    Mul(self.left, self.right.deriv(var)))
    def simplify(self):
        """
        Simpify the expression
        """
        result = Mul(self.left.simplify(), self.right.simplify())
        if isinstance(result.left, Num) and isinstance(result.right, Num):
            return Num(result.left.n * result.right.n)
        if isinstance(result.left, Num):
            if result.left.n == 0:
                return Num(0)
            if result.left.n == 1:
                return result.right
        if isinstance(result.right, Num):
            if result.right.n == 1:
                return result.left
            if result.right.n == 0:
                return Num(0)
        return result

class Div(BinOp):
    """
    Division operation
    """
    special = True
    def __init__(self, left, right):
        BinOp.__init__(self, left, right)
        self.operation = "/"
        self.level = 2
    def eval(self, mapping):
        """
        Evaluate the expression
        """
        return self.left.eval(mapping) / self.right.eval(mapping)
    def deriv(self, var):
        """
        Take the derivative by its derivative rule
        """
        return Div(Sub(Mul(self.left.deriv(var), self.right),
                        Mul(self.left, self.right.deriv(var)))
                   , Mul(self.right, self.right))
    def simplify(self):
        """
        Simpify the expression
        """
        result = Div(self.left.simplify(), self.right.simplify())
        if isinstance(result.left, Num) and isinstance(result.right, Num):
            return Num(result.left.n / result.right.n)
        if isinstance(result.right, Num) and result.right.n == 1:
            return result.left
        if isinstance(result.left, Num) and result.left.n == 0:
            return Num(0)
        return result
def make_expression(exp):
    return parse(tokenize(exp))
def tokenize(exp):
    """
    >>> tokenize("(x * (2.5 + 3))")
    ['(', 'x', '*', '(', '2.5', '+', '3', ')', ')']
    """
    result = ""
    for i in exp:
        if i in "()":
            result += " " + i + " "
        else:
            result += i
    return result.split()

def parse(tokens):
    """
    Parse a list of tokens into an appropriate instance of Expr
    """
    def parse_expression(index):
        try:
            return Num(float(tokens[index])), index+1
        except:
            if tokens[index] not in "+-*/()":
                return Var(tokens[index]), index+1
            exp, i = parse_expression(index+1)
            exp2, i2 = parse_expression(i+1)
            operation = tokens[i]
            end = i2 + 1
            op = {"+":Add(exp, exp2), "-":Sub(exp, exp2), "*":Mul(exp, exp2),"/":Div(exp, exp2)}
            return op[operation], end
            # if operation == "+":
            #     return Add(exp, exp2), end
            # if operation == '-':
            #     return Sub(exp, exp2), end
            # if operation == "*":
            #     return Mul(exp, exp2), end
            # if operation == "/":
            #     return Div(exp, exp2), end
    parsed_expression, _ = parse_expression(0)
    return parsed_expression

if __name__ == "__main__":
    z = Add(Var('x'), Sub(Var('y'), Num(2)))
    print(str(z))
    print(repr(z))
    z = Mul(Var('x'), Add(Var('y'), Var('z')))
    print(str(z))
    z = Div(Mul(Num(7), Var("A")), Num(1))
    print(str(z))

    inp = Add(Var("z"), Add(Var("x"), Num(1)))
    print(inp.eval({"z": -596, "x": -554}))
    #print(inp.eval({"z":500}))

    print(Sub(Num(10), Add(Num(4.0), Var('x'))) == Sub(Num(10), Add(Num(4), Var('x'))))
    print(tokenize("(x * (2.5 + 3))"))
