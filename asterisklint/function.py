from .variable import SliceMixin, Var


class ReadFunc(Var):
    """
    A special case of VarSlice where a function call is evaluated.

    The ReadFunc is different from the WriteFunc in that the ReadFunc
    has surrounding ${} tokens and allows slicing.
    """
    def __init__(self, func=None, args=None):
        assert func is not None and args is not None

        # The "convenience" strjoin in Var getslice creates trouble for
        # us here: args can be a list or a simple iterable.
        if isinstance(args, list):
            func_and_args = [func, '('] + args + [')']
        else:
            func_and_args = [func, '(', args, ')']

        super().__init__(name=Var.join(func_and_args))

        self.func = func
        self.args = args


class ReadFuncSlice(SliceMixin, ReadFunc):
    pass
