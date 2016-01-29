0.2.1 (2016-01-29)
~~~~~~~~~~~~~~~~~~

* Don't look in __init__ for custom commands.

0.2.0 (2016-01-29)
~~~~~~~~~~~~~~~~~~

* Add partial func_odbc checking.
* Add new command: func_odbc-show
* Do func_odbc checks for modules-show and dialplan-show, so you don't
  get flooded with E_FUNC_MISSING errors if you use func_odbc.
* Fix a few variable/dialplan parsing bugs, improve some.

0.1.0 (2016-01-15)
~~~~~~~~~~~~~~~~~~

* Initial release.
* The following commands are available:
  dialplan-check, dialplan-show, modules-show
