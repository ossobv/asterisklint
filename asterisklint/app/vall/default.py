from ...application import W_APP_BALANCE

# TODO: instead of where, we should pass a context object that context
# could include a where, and also a list of classes where we can store
# significant info like "label" when there is a goto/gosub that jumps to
# one.


class Default(object):
    @property
    def name(self):
        return self.__class__.__name__

    def __call__(self, data, where):
        try:
            self.check_balance(data)
        except ValueError:
            W_APP_BALANCE(where)

    @staticmethod
    def check_balance(app):
        # TODO: we don't check backslash escapes here, should we?
        # TODO: write proper tests for this?
        arr = ['X']
        for char in app:
            if char == '"':
                if arr[-1] == '"':
                    arr.pop()
                elif arr[-1] == "'":
                    pass
                else:
                    arr.append('"')
            elif char == "'":
                if arr[-1] == "'":
                    arr.pop()
                elif arr[-1] == '"':
                    pass
                else:
                    arr.append("'")
            elif char in '({[':
                if arr[-1] in '\'"':
                    pass
                else:
                    arr.append(char)
            elif char in ')}]':
                left = '({['[')}]'.index(char)]
                if arr[-1] in '\'"':
                    pass
                else:
                    if arr[-1] == left:
                        arr.pop()
                    else:
                        raise ValueError(''.join(arr[1:]))
        if arr != ['X']:
            raise ValueError(''.join(arr[1:]))


if True:
    class DumpChan(Default):
        pass

    class Hangup(Default):
        pass

    class NoOp(Default):
        pass

    class Verbose(Default):
        pass


def register(app_loader):
    # Called by the app_loader.
    for app in (Default, DumpChan, Hangup, NoOp, Verbose):
        app_loader.register(app())
