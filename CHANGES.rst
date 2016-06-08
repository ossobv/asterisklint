0.3.0 (2016-06-08)
~~~~~~~~~~~~~~~~~~

* Add preliminary Goto/Gosub scanning: the dialplan-check now tries to
  find non-existent goto destinations. New error classes:
  E_DP_GOTO_CONTEXT_NOLABEL, E_DP_GOTO_NOCONTEXT, E_DP_GOTO_NOLABEL,
  W_DP_GOTO_CONTEXT_NOEXTEN.
* Add preliminary app argument checking. New error classes:
  E_APP_ARG_IFCONST, E_APP_ARG_IFEMPTY, E_APP_ARG_SYNTAX.
* Add new command: ident-scan. It lists used contexts, labels and
  variables and does a poor attempt at finding typo's by comparing
  them against each other.
* Add Asterisk apps: NoCDR, Record.
* The commands taking a path to extensions.conf now default to scanning
  for it in the current directory.
* Python3.5 testcase compatibility fix.

0.2.1 (2016-01-29)
~~~~~~~~~~~~~~~~~~

* Don't look in __init__ for custom commands.

0.2.0 (2016-01-29)
~~~~~~~~~~~~~~~~~~

* Add partial func_odbc checking.
* Add new command: func_odbc-check
* Do func_odbc checks for modules-show and dialplan-show, so you don't
  get flooded with E_FUNC_MISSING errors if you use func_odbc.
* Fix a few variable/dialplan parsing bugs, improve some.

0.1.0 (2016-01-15)
~~~~~~~~~~~~~~~~~~

* Initial release.
* The following commands are available:
  dialplan-check, dialplan-show, modules-show
