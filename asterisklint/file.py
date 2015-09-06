# vim: set ts=8 sw=4 sts=4 et ai:
from .defines import ErrorDef, WarningDef
from .where import Where


if True:  # cheat to trick flake8 into letting me do single blank lines
    class E_ENC_NOT_UTF8(ErrorDef):
        message = 'expected UTF-8 encoding, got something else'

    class W_FF_DOS_EOFCRLF(WarningDef):
        message = 'unexpected trailing CRLF in DOS file format'

    class W_FF_DOS_BARELF(WarningDef):
        message = 'unexpected bare LF in DOS file format'

    class W_FF_UNIX_CRLF(WarningDef):
        message = 'unexpected CRLF in UNIX file format'

    class W_FF_UNIX_NOLF(WarningDef):
        message = 'unexpected line without LF in UNIX file format'


class BinFileReader(object):
    """
    Reads a file from disk.
    """
    def __init__(self, filename=None):
        self.filename = filename

    def __iter__(self):
        prev_where, prev_data = None, None

        with open(self.filename, 'rb') as fp:
            for i, line in enumerate(fp):
                if prev_where:
                    yield prev_where, prev_data

                prev_where = Where(self.filename, i + 1, line)
                prev_data = line

        if prev_where:
            prev_where.last_line = True
            yield prev_where, prev_data


class EncodingReader(object):
    """
    Decodes lines from UTF-8, the one true encoding.
    """
    def __iter__(self):
        for where, data in super(EncodingReader, self).__iter__():
            try:
                data = data.decode('utf-8')
            except UnicodeDecodeError:
                E_ENC_NOT_UTF8(where)
                data = data.decode('cp1252')  # or latin1? or 9?
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
                    W_FF_DOS_EOFCRLF(where)
                elif has_lf and not has_crlf:
                    W_FF_DOS_BARELF(where)
            else:
                if where.last_line and not has_lf:
                    W_FF_UNIX_NOLF(where)
                elif has_crlf:
                    W_FF_UNIX_CRLF(where)

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


class FileReader(FileformatReader, EncodingReader, BinFileReader):
    pass
