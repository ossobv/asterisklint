from .variable import Var


class Expr(Var):
    """
    A special case of Var where an expression is evaluated.

    TODO: complain about (expr);
    - excess whitespace
    - no agreement on quotes on either side of expression
    - bad/unknown operators
    - joined expressions (expr in expr, which is not needed, because you
      can use parens)
    """
    def __init__(self, expression=None):  # drop start and length args
        super().__init__(name=expression)

    def __str__(self):
        if self.name:
            return '$[{}]'.format(self.name)
        return super().__str__()
