from .variable import Var


class Func(Var):
    """
    A special case of Var where a function call is evaluated.

    TODO: this shouldn't be here probably, since we need the more
    complicated function loaders from elsewhere..
    """
    def __init__(self, func_and_args=None):
        super().__init__(name=func_and_args)
