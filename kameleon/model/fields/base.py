################################################################################
# MIT License
#
# Copyright (c) 2017 Jean-Charles Fosse & Johann Bigler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
################################################################################

class attrdict(dict):
    def __getattr__(self, attr):
        return self[attr]

OP = attrdict(
    AND='and',
    OR='or',
    ADD='+',
    SUB='-',
    MUL='*',
    DIV='/',
    BIN_AND='&',
    BIN_OR='|',
    XOR='^',
    MOD='%',
    EQ='=',
    LT='<',
    LTE='<=',
    GT='>',
    GTE='>=',
    NE='!=',
    IN='in',
    NOT_IN='not in',
    IS='is',
    IS_NOT='is not',
    LIKE='like',
    ILIKE='ilike',
    BETWEEN='between',
    REGEXP='regexp',
    CONCAT='||',
)

OP_MAP = {
        OP.EQ: '=',
        OP.LT: '<',
        OP.LTE: '<=',
        OP.GT: '>',
        OP.GTE: '>=',
        OP.NE: '!=',
        OP.IN: 'IN',
        OP.NOT_IN: 'NOT IN',
        OP.IS: 'IS',
        OP.IS_NOT: 'IS NOT',
        OP.BIN_AND: '&',
        OP.BIN_OR: '|',
        OP.LIKE: 'LIKE',
        OP.ILIKE: 'ILIKE',
        OP.BETWEEN: 'BETWEEN',
        OP.ADD: '+',
        OP.SUB: '-',
        OP.MUL: '*',
        OP.DIV: '/',
        OP.XOR: '#',
        OP.AND: 'AND',
        OP.OR: 'OR',
        OP.MOD: '%',
        OP.REGEXP: 'REGEXP',
        OP.CONCAT: '||',
    }

class Node(object):
    """
    Base-class for any part of a query which shall be composable.
    """
    _node_type = 'node'

    def __init__(self):
        self._negated = False
        self._alias = None
        self._bind_to = None
        self._ordering = None  # ASC or DESC.

    def __eq__(self, rhs):
        if rhs is None:
            return Expression(self, OP.IS, None)
        return Expression(self, OP.EQ, rhs)

    def _e(op, inv=False):
        """
        Lightweight factory which returns a method that builds an Expression
        consisting of the left-hand and right-hand operands, using `op`.
        """
        def inner(self, rhs):
            if inv:
                return Expression(rhs, op, self)
            return Expression(self, op, rhs)

        return inner

    __and__ = _e(OP.AND)
    __or__ = _e(OP.OR)

    __add__ = _e(OP.ADD)
    __sub__ = _e(OP.SUB)
    __mul__ = _e(OP.MUL)
    __div__ = __truediv__ = _e(OP.DIV)
    __xor__ = _e(OP.XOR)
    __radd__ = _e(OP.ADD, inv=True)
    __rsub__ = _e(OP.SUB, inv=True)
    __rmul__ = _e(OP.MUL, inv=True)
    __rdiv__ = __rtruediv__ = _e(OP.DIV, inv=True)
    __rand__ = _e(OP.AND, inv=True)
    __ror__ = _e(OP.OR, inv=True)
    __rxor__ = _e(OP.XOR, inv=True)

    __lt__ = _e(OP.LT)
    __le__ = _e(OP.LTE)
    __gt__ = _e(OP.GT)
    __ge__ = _e(OP.GTE)
    __lshift__ = _e(OP.IN)
    __rshift__ = _e(OP.IS)
    __mod__ = _e(OP.LIKE)
    __pow__ = _e(OP.ILIKE)

    def is_null(self, is_null=True):
        if is_null:
            return Expression(self, OP.IS, None)
        return Expression(self, OP.IS_NOT, None)

    def not_in(self, rhs):
        return Expression(self, OP.NOT_IN, rhs)

class Field(Node):
    """
    A column on a table.
    """
    _node_type = 'field'

    def __init__(self, unique=False, salt=False):
        super(Field, self).__init__()

        # This field is unique in this table
        self.unique = unique

        # This field should be encrypted using bcrypt
        self.salt = salt

        # Column name
        self.name = None

        # Field Model
        self.model_class = None

    def get_db_field(self):
        if self.model_class._meta.database:
            return self.model_class._meta.database.TYPES[self.TYPE]

        return self.TYPE

    def add_to_model(self, model_class, name):
        self.name = name
        self.model_class = model_class
        model_class._meta.add_field(self)

class Expression(Node):
    """
    A binary expression, e.g `foo + 1` or `bar < 7`.
    """
    _node_type = 'expression'

    def __init__(self, lhs, op, rhs):
        super(Expression, self).__init__()

        # Left operator
        self.lhs = lhs

        # Operator
        self.op = op

         # Right operator
        self.rhs = rhs

    def parse(self):
        if isinstance(self.lhs, Field):
            if isinstance(self.rhs, list):
                _list = "', '".join(self.rhs)
                return "{0}.{1} {2} ('{3}')".format(self.lhs.model_class._meta.table_name, self.lhs.name, self.op, _list)
            elif self.rhs == None:
                return "{0}.{1} {2} NULL".format(self.lhs.model_class._meta.table_name, self.lhs.name, self.op)
            return "{0}.{1} {2} '{3}'".format(self.lhs.model_class._meta.table_name, self.lhs.name, self.op, self.rhs)
        elif isinstance(self.lhs, Expression) and isinstance(self.rhs, Expression):
            left = self.lhs.parse()
            right = self.rhs.parse()
            return "({0} {1} {2})".format(left, self.op, right)
        else:
            print("ERROR: Logic error")
