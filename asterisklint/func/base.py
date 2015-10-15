class FuncBase(object):
    @property
    def name(self):
        return self.__class__.__name__

    @property
    def module(self):
        return self.__module__.rsplit('.', 1)[-1]

    def __call__(self, data, where):
        pass
