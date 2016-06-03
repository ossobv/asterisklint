Asterisk PBX configuration syntax checker
=========================================

Asterisklint is a suite of tools to check syntax of your Asterisk PBX
configuration files.

Alright, enough talking. Some examples please.


Invocation
----------

.. code-block:: console

    $ asterisklint
    usage: asterisklint [-h] COMMAND
    asterisklint: error: the following arguments are required: COMMAND

    $ asterisklint ls
    builtin:
      ls                    List available commands.

    /usr/lib/python/dist-packages:
      dialplan-check        Do sanity checks on dialplan. Takes 'extensions.conf'
                            as argument. Suppress error classes using ALINT_IGNORE.
      dialplan-show         Show dialplan like Asterisk does with CLI command
                            "dialplan show". Takes 'extensions.conf' as argument.
      func_odbc-check       Do sanity checks on func_odbc.conf. Takes
                            'func_odbc.conf' as argument. Suppress error classes
                            using ALINT_IGNORE.
      ident-scan            Report similarly named contexts, labels and variables.
                            Takes 'extensions.conf' as argument. All parse errors
                            are suppressed.
      modules-show          Show which modules, apps and functions are used by the
                            dialplan. Takes 'extensions.conf' as argument.

    Place custom commands in ~/.asterisklint/asterisklint/commands.


Take this little dialplan snippet, that we'll call ``extensions.conf``::

    [default]
    exten => _8[2-9]x,1,NoOp
     same => n,GoSub(somewhere,s,1(argument1,argument2)
     same => n,Payback(audiofile)

Now run the ``dialplan-check`` command on it:

.. code-block:: console

    $ ALINT_IGNORE=H_DP_ asterisklint dialplan-check extensions.conf
    extensions.conf:2 H_PAT_NON_CANONICAL: pattern '_8[2-9]x' is not in the canonical form '_8NX'
    extensions.conf:3 W_APP_BAD_CASE: app 'GoSub' does not have the proper Case 'Gosub'
    extensions.conf:3 W_APP_BALANCE: app data '1(argument1,argument2' looks like unbalanced parentheses/quotes/curlies
    extensions.conf:4 E_APP_MISSING: app 'Payback' does not exist, dialplan will halt here!
    extensions.conf:3 E_DP_GOTO_NOCONTEXT: context not found for goto to somewhere, s, 1

It had a lot to complain about that little snippet. But it was right. We
even suppressed two hints about a missing ``[general]`` and ``[global]``
context using ``ALINT_IGNORE``.

Not everything it checks is documented, and it does not check everything
that we like yet. But it's a start. Bug reports are welcome. Feature requests
prefer to be accompanied by a patch :-)

Try out ``modules-show`` if you use ``autoload=no`` in your ``modules.conf``.

All commands show help if asked:

.. code-block:: console

    $ asterisklint modules-show --help
    usage: asterisklint modules-show [-h] [--func-odbc FUNC_ODBC_CONF]
                                     [EXTENSIONS_CONF]

    Show which modules, apps and functions are used by the dialplan. Useful when
    you use autoload=no in your modules.conf. Beware that you do need more modules
    than just these listed.

    positional arguments:
      EXTENSIONS_CONF       path to extensions.conf

    optional arguments:
      -h, --help            show this help message and exit
      --func-odbc FUNC_ODBC_CONF
                            path to func_odbc.conf, will be read automatically if
                            found in same the same dir as extensions.conf; set
                            empty to disable


Installation
------------

Installation is a matter of ``python3 setup.py install``. Or, for more convenience,
install a PyPI uploaded version through ``pip3(1)``:

.. code-block:: console

    $ sudo pip3 install asterisklint
    ...
    Successfully installed asterisklint


The ``dialplan-check`` comes in handy as a git commit hook, for example
``.git/hooks/pre-commit``:

.. code-block:: sh

    #!/bin/sh
    export ALINT_IGNORE=  # adjust as needed

    asterisklint dialplan-check PATH/TO/extensions.conf
    ret=$?
    if test $ret -ne 0; then
        echo >&2
        echo 'One or more dialplan syntax errors. Please fix before committing.' >&2
        exit $ret
    fi

    exit 0


TODO
----

* Func_odbc parsing improvements:
  - check for missing synopsis/syntax (compare syntax to ARGn count)
  - check for correct usage of VAL (write only) and ARG and missing SQL_ESC
  - yield the odbc functions instead of contexts like it does now
  (See more in func_odbc.py.)
* Improve documentation as needed.
* Expression parsing.
* Function argument parsing.
* Recursive #includes probably make asterisklint run out of stack.
* Trim CALLERID match (as used in FreePBX dialplan).
* Add functions DB, DB_EXISTS, MD5 (as used in FreePBX dialplan).
* Add apps Authenticate, AGI (as used in FreePBX dialplan).
* Scan for missing dialplan-includes.
* Add checks for recursive dialplan-includes.
* For the Goto/Gosub-visiting:
  - Attempt to match contexts by regex if there are $VARs involved?
  - Allow a "noqa" style exceptions to be placed in a comment?
* Add ``app-check`` command to do dialplan checks of individual lines.
* Add ``expr-check`` command to do expression (``$[...]``) checks.
* Allow multiline variables using += (key=val; key+=more-val).
* Investigate whether exten=>s,n(label)... exten=>s,label+10... is valid.
* Before 1.0, start adding versioning -- including semver -- so users can
  depend on a stable API from their custom scripts. Also version the scripts
  (commands) so they won't talk to older/newer libs if that poses a problem.


BUGS
----

* The library is very much in flux. Don't expect it to stabilize any time
  soon. Pay attention to versions!
* Multiline comments (``;-- ... --;``) are unsupported. Does anyone use those?
* Limits aren't checked (dialplan lines are limited at 255 or 8191 bytes
  for LOW_MEMORY and normal mode respectively).
* The library/suite is Python3 only. Right now the effort to make it Python2
  compatible is larger than the demand. In the future Python2 compatibility
  will become even less relevant.


Author
------

Walter Doekes, OSSO B.V. 2015,2016
