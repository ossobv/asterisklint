from ..base import AppBase, IfStyleApp

# In the following commit -- between Asterisk 1.4 and Asterisk 1.6.x --
# not only did the default App argument delimiter change from pipe (|)
# to comma (,), but also the ExecIf change to GotoIf-style syntax, using
# a question mark (?).
#
# > commit 55b1ee298e926c594f45456e5afbc25c79e3889b
# > Author: Tilghman Lesher <tilghman@CENSORED>
# > Date:   Mon Jul 23 19:51:41 2007 +0000
#
# > Merge the dialplan_aesthetics branch.  Most of this patch simply
# > converts applications using old methods of parsing arguments to
# > using the standard macros.  However, the big change is that the
# > really old way of specifying application and arguments separated by
# > a comma will no longer work (e.g. NoOp,foo|bar).  Instead, the way
# > that has been recommended since long before 1.0 will become the only
# > method available (e.g. NoOp(foo,bar).
# >
# > git-svn-id: https://origsvn.digium.com/svn/asterisk/trunk@76703
# >   65c4cc65-6c06-0410-ace0-fbb531ad65f3


class Exec(AppBase):
    pass


class ExecIf(IfStyleApp):
    pass


class TryExec(AppBase):
    pass


def register(app_loader):
    for app in (
            Exec, ExecIf, TryExec):
        app_loader.register(app())
