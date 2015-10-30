from tempfile import NamedTemporaryFile
import os


class FileMutatorBase(object):
    """
    Base class that mutates config files. You override this and
    implement your own process_issue method.

    Example::

        class MyMutator(FileMutatorBase):
            def process_issue(self, issue, inline, outfile):
                outfile.write(issue.changes_based_on_line(inline))

        mutator = MyMutator(
            issues_per_file={
                'somefile.conf': [
                    Issue(lineno=3, ...), Issue(lineno=5, ...)])
        mutator.print_summary()
        mutator.request_permission_and_process()
    """
    def __init__(self, issues_per_file):
        self.issues_per_file = issues_per_file
        self.filenames = list(sorted(self.issues_per_file.keys()))

    def request_permission_and_process(self):
        if not self.issues_per_file:
            print("Your dialplan has no issues. We're done here.")
            return

        print('The following files have issues:')
        print('  {}'.format('\n  '.join(self.filenames)))
        yesno = input('Update all [y/n] ? ')

        if yesno != 'y':
            print('Aborted.')
            return

        self.process()
        print('Done')

    def process(self):
        for filename in self.filenames:
            self.process_file(filename)

    def process_file(self, filename):
        # Place the tempfile in the same dir, so renaming works
        # (same device).
        tempout = NamedTemporaryFile(
            dir=os.path.dirname(filename), mode='wb', delete=False)

        issues = self.issues_per_file[filename]
        try:
            issueptr = 0
            issue = issues[issueptr]
            with open(filename, 'rb') as file_:
                for lineno, line in enumerate(file_):
                    if issue and lineno == issue.lineno:
                        # Do actual work on the issue.
                        self.process_issue(
                            issue=issue,
                            inline=line,
                            outfile=tempout)

                        # Jump to the next issue.
                        issueptr += 1
                        if issueptr < len(issues):
                            issue = issues[issueptr]
                        else:
                            issue = None
                    else:
                        tempout.write(line)
            tempout.flush()
        except:
            tempout.close()
            os.unlink(tempout.name)
            raise

        # Awesome, we've succeeded. Atomic move time!
        tempout.close()

        # Update file permissions.
        srcstat = os.stat(tempout.name)
        dststat = os.stat(filename)
        if (srcstat.st_uid != dststat.st_uid or
                srcstat.st_gid != dststat.st_gid):
            os.chown(tempout.name, dststat.st_uid, dststat.st_gid)
        if srcstat.st_mode != dststat.st_mode:
            os.chmod(tempout.name, dststat.st_mode)

        print('Overwriting', filename, '...')
        os.rename(tempout.name, filename)

    def process_issue(self, issue, inline, outfile):
        raise NotImplementedError()
