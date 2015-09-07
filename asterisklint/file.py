# vim: set ts=8 sw=4 sts=4 et ai:
from .defines import ErrorDef, WarningDef
from .where import Where


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
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

    class E_FILE_UTF8_BAD(ErrorDef):
        message = 'expected UTF-8 encoding, got something else'


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


class AstCommentReader(object):
    # Todo.. strip all comments
    # Todo.. decode the non-comments (backslash remove)
    # Todo.. multiline?
    # Remove whitespace..
    # Todo.. complain about missing whitespace between objects.
    pass


class FileReader(FileformatReader, NoCtrlReader, EncodingReader,
                 BinFileReader):
    pass
