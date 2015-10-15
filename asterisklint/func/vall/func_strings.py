from ..base import FuncBase


class ARRAY(FuncBase):
    pass


class CSV_QUOTE(FuncBase):
    pass


class EVAL(FuncBase):
    pass


class FIELDNUM(FuncBase):
    pass


class FIELDQTY(FuncBase):
    pass


class FILTER(FuncBase):
    pass


class HASH(FuncBase):
    pass


class HASHKEYS(FuncBase):
    pass


class KEYPADHASH(FuncBase):
    pass


class LEN(FuncBase):
    pass


class LISTFILTER(FuncBase):
    pass


class PASSTHRU(FuncBase):
    pass


class POP(FuncBase):
    pass


class PUSH(FuncBase):
    pass


class QUOTE(FuncBase):
    pass


class REGEX(FuncBase):
    pass


class REPLACE(FuncBase):
    pass


class SHIFT(FuncBase):
    pass


class STRFTIME(FuncBase):
    pass


class STRPTIME(FuncBase):
    pass


class STRREPLACE(FuncBase):
    pass


class TOLOWER(FuncBase):
    pass


class TOUPPER(FuncBase):
    pass


class UNSHIFT(FuncBase):
    pass


def register(func_loader):
    for func in (
            ARRAY,
            CSV_QUOTE,
            EVAL,
            FIELDNUM,
            FIELDQTY,
            FILTER,
            HASH,
            HASHKEYS,
            KEYPADHASH,
            LEN,
            LISTFILTER,
            PASSTHRU,
            POP,
            PUSH,
            QUOTE,
            REGEX,
            REPLACE,
            SHIFT,
            STRFTIME,
            STRPTIME,
            STRREPLACE,
            TOLOWER,
            TOUPPER,
            UNSHIFT,
            ):
        func_loader.register(func())
