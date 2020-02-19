0.4.2 (2020-02-19)
~~~~~~~~~~~~~~~~~~

Bug fixes:

* Don't choke on too many Gosub arguments.
* Fixes for various python 3 versions.

Improvements:

* Added PJSIP_HEADER, PJSIP_AOR, PJSIP_CONTACT, PJSIP_ENDPOINT.

0.4.1 (2018-10-10)
~~~~~~~~~~~~~~~~~~

Bug fixes:

* Cope with ${vars} in FUNC() arguments.
* Fix typo's in func_odbc-check.
* Speedup in dialplan goto-parsing.
* Unbreak custom command support.

Improvements:

* Add missing app_milliwatt, app_mysql, app_originate,
  func_audiohookinherit, func_volume_register.
* Add preliminary func_odbc-annotate command; not feature complete.
* Add the (now obsolete) vg.py contrib command which alters certain file
  reading functions so a slightly different syntax is accepted.
* Check applications called in ExecIf().

0.4.0 (2017-04-05)
~~~~~~~~~~~~~~~~~~

Bug fixes:

* When doing dialplan-file mutations, operate on the symlink target
  instead of replacing the symlink.
* Don't install README files into /usr, but in
  /usr/share/doc/asterisklint (or with a different prefix).
* Also search in included contexts for priority labels.

Improvements:

* Add various apps:
  - Authenticate, ControlPlayback, PickupChan
  - PickupOld1v4 (a workaround, see ASTERISK-26464)
  - VoiceMailPlayMsg, VMSayName,
  - ContinueWhile, EndWhile, ExitWhile, While,
  - AGI, DeadAGI, EAGI,
  - StopMusicOnHold
* Add various functions:
  - DB, DB_EXISTS, DB_KEYS, DB_DELETE,
  - MD5, TIMEOUT
  - LOCAL, LOCAL_PEEK, STACK_PEEK
* Add initial checks of function parameters: nothing more than the
  parentheses check we already used on undefined apps.
* Add application Set() support. Add function SET() support. This also
  enables checking calls to writable functions.
* Allow both the "BackGround" and "Background" spelling, as long as
  you choose one consistently.
* A bunch of refactoring to make BetterCodeHub happy. If you've made
  custom subcommands, look at the MainBase class.
* Add test with Asterisk 13 sample dialplan as input.
* Add web frontend into repository.

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
