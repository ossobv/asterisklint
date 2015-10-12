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
            W_APP_BALANCE(where, data=data)

    @staticmethod
    def check_balance(data):
        # TODO: we don't check backslash escapes here, should we?
        # TODO: write proper tests for this?
        arr = ['X']
        for char in data:
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

    @staticmethod
    def separate_args(data, delim=',', remove_quotes_backslashes=True):
        """
        #define AST_STANDARD_APP_ARGS(...) => separate_args(',', True)
        #define AST_STANDARD_RAW_ARGS(...) => separate_args(',', False)

        SOURCE: main/app.c -- __ast_app_separate_args()

        TODO: we should separate args using a more sensible approach as
        well, so we can warn on inconsistencies.
        """
        brackets = 0
        parens = 0
        quotes = False
        skipnext = False

        ret = [[]]
        start = 0
        for i, char in enumerate(data):
            if skipnext:
                skipnext = False
            elif char == '[':
                brackets += 1
            elif char == ']':
                if brackets:
                    brackets -= 1
            elif char == '(':
                parens += 1
            elif char == ')':
                if parens:
                    parens -= 1
            elif char == '"' and delim != '"':
                quotes = not quotes
                if remove_quotes_backslashes:
                    ret[-1].append(data[start:i])
                    start = i + 1
            elif char == '\\':
                if remove_quotes_backslashes:
                    ret[-1].append(data[start:i])
                    start = i + 1
                skipnext = True
            elif char == delim and not (brackets or parens or quotes):
                ret[-1].append(data[start:i])
                start = i + 1
                ret.append([])  # start on next arg

        # Append leftover args.
        ret[-1].append(data[start:])

        # Squash args.
        ret = [''.join(i) for i in ret]

        return ret
