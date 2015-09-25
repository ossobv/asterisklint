from ..application import W_APP_BALANCE

# TODO: instead of where, we should pass a context object that context
# could include a where, and also a list of classes where we can store
# significant info like "label" when there is a goto/gosub that jumps to
# one.


class AppBase(object):
    @property
    def name(self):
        return self.__class__.__name__

    @property
    def module(self):
        return self.__module__.rsplit('.', 1)[-1]

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
