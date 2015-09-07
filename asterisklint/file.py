# vim: set ts=8 sw=4 sts=4 et ai:
from .defines import ErrorDef, WarningDef
from .where import Where


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class E_FILE_UTF8_BAD(ErrorDef):
        message = 'expected UTF-8 encoding, got something else'

    class W_FILE_BS_EOL(WarningDef):
        message = 'backslash at EOL, not supported'  # XXX?

    class W_FILE_CTRL_CHAR(WarningDef):
        message = 'unexpected control character found'

    class W_FILE_DOS_EOFCRLF(WarningDef):
        message = 'unexpected trailing CRLF in DOS file format'

    class W_FILE_DOS_BARELF(WarningDef):
        message = 'unexpected bare LF in DOS file format'

    class W_FILE_UNIX_CRLF(WarningDef):
        message = 'unexpected CRLF in UNIX file format'

    class W_FILE_UNIX_NOLF(WarningDef):
        message = 'unexpected line without LF in UNIX file format'

    class W_WSH_EOL(WarningDef):
        message = 'unexpected trailing whitespace'


class BinFileReader(object):
    """
    Reads a binary opened file.
    """
    def __init__(self, fp=None):
        if hasattr(fp, 'mode'):
            assert 'b' in fp.mode, 'expected binary opened file'
        self.fp = fp
        self.filename = fp.name

    def __iter__(self):
        prev_where, prev_data = None, None

        for i, line in enumerate(self.fp):
            if prev_where:
                yield prev_where, prev_data

            prev_where = Where(self.filename, i + 1, line)
            prev_data = line

        if prev_where:
            prev_where.last_line = True
            yield prev_where, prev_data

        if hasattr(self.fp, 'close'):
            self.fp.close()


class EncodingReader(object):
    """
    Decodes lines from UTF-8, the one true encoding.
    """
    def __iter__(self):
        for where, data in super(EncodingReader, self).__iter__():
            try:
                data = data.decode('utf-8')
            except UnicodeDecodeError:
                E_FILE_UTF8_BAD(where)
                data = data.decode('cp1252')  # or latin1? or 9?
            yield where, data


class NoCtrlReader(object):
    """
    Checks for unusual control characters.
    """
    # all, except \r (0d), \n (0a), \t (09)
    illegal = set('\x00\x01\x02\x03\x04\x05\x06\x07'
                  '\x08'      '\x0b\x0c'  '\x0e\x0f'
                  '\x10\x11\x12\x13\x14\x15\x16\x17'
                  '\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f')

    def __iter__(self):
        for where, data in super(NoCtrlReader, self).__iter__():
            charset = set(data)
            union = charset & self.illegal
            if union:
                W_FILE_CTRL_CHAR(where)

            yield where, data


class FileformatReader(object):
    """
    TODO: allow one to specify legal line endings (unix vs dos)
    """
    def __iter__(self):
        is_dos = None

        for where, data in super(FileformatReader, self).__iter__():
            has_crlf = data.endswith('\r\n')
            has_lf = data.endswith('\n')

            if is_dos is None:
                is_dos = (has_crlf or not has_lf)

            if is_dos:
                if where.last_line and has_crlf:
                    W_FILE_DOS_EOFCRLF(where)
                elif has_lf and not has_crlf:
                    W_FILE_DOS_BARELF(where)
            else:
                if where.last_line and not has_lf:
                    W_FILE_UNIX_NOLF(where)
                elif has_crlf:
                    W_FILE_UNIX_CRLF(where)

            if has_crlf:
                data = data[0:-2]
            elif has_lf:
                data = data[0:-1]

            yield where, data


class AsteriskCommentReader(object):
    """
    Unescapes backslash escapes and splits the data from the comments.

    TODO: also parse multiline asterisk comments
    """
    @staticmethod
    def simple_comment_split(data):
        try:
            i = data.index(';')
        except ValueError:
            return data, ''
        while i > 0 and data[i - 1] in ' \t':
            i -= 1
        return data[0:i], data[i:]

    def __iter__(self):
        for where, data in super(AsteriskCommentReader, self).__iter__():
            # Shortcut if we don't do any escaping.
            if '\\' not in data:
                if data.endswith(tuple(' \t')):
                    W_WSH_EOL(where)
                    data = data.rstrip(' \t')
                data, comment = self.simple_comment_split(data)
                yield where, data, comment
                continue

            # Unescape the values manually.
            is_escaped = False
            out = []
            for i, ch in enumerate(data):
                if is_escaped:
                    is_escaped = False
                    out.append(ch)
                    out.append('')  # don't backward remove past this
                elif ch == '\\':
                    is_escaped = True
                elif ch == ';':
                    rest = list(data[i:])
                    break
                else:
                    out.append(ch)
            else:
                if is_escaped:
                    W_FILE_BS_EOL(where)
                rest = []

            # Seek backwards from i, because all blanks go with the
            # comments.
            while out and out[-1] and out[-1] in ' \t':
                rest.insert(0, out.pop())
            if rest and rest[-1] in ' \t':
                W_WSH_EOL(where)
                while rest and rest[-1] in ' \t':
                    rest.pop()

            yield where, ''.join(out), ''.join(rest)


class FileReader(AsteriskCommentReader, FileformatReader, NoCtrlReader,
                 EncodingReader, BinFileReader):
    pass
