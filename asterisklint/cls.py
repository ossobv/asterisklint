class Singleton(type):
    """
    Create singleton classes. Usage::

        class MyClass(metaclass=Singleton):
            ...

        MyClass().do_stuff()

    If your class implements the reinit() method, it will be called with
    the same arguments as to __init__ in case it was already created.
    There you may evaluate if the args/kwargs are allowed and/or need
    updating::

        def reinit(self, optional_config=None):
            if optional_config and self.config != optional_config:
                raise ProgrammingError("You cannot switch config!")
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            ret = cls._instances[cls] = super().__call__(*args, **kwargs)
        else:
            ret = cls._instances[cls]
            if hasattr(ret, 'reinit'):
                ret.reinit(*args, **kwargs)

        return ret
