Asterisk PBX configuration syntax checker
=========================================

Asterisklint is a suite of tools to check syntax of your Asterisk PBX
configuration files.

Alright, enough talking. Some examples please.


Invocation
----------

.. code-block:: console

    $ asterisklint
    usage: asterisklint [-h] CMD
    asterisklint: error: the following arguments are required: CMD

    $ asterisklint ls
    builtin:
      ls                    List available commands.

    /usr/lib/python/dist-packages:
      dialplan-check        Do sanity checks on dialplan. Takes 'extensions.conf'
                            as argument. Suppress error classes using ALINT_IGNORE.
      dialplan-show         Show dialplan like Asterisk does with CLI command
                            "dialplan show". Takes 'extensions.conf' as argument.
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
    extensions.conf:3 W_APP_BALANCE: app data 'somewhere,1,s(argument1,argument2' looks like unbalancedparenthesis/quotes/curlies
    extensions.conf:4 E_APP_MISSING: app 'Payback' does not exist, dialplan will halt here!

It had a lot to complain about that little snippet. But it was right. We
even suppressed two hints about a missing ``[general]`` and ``[global]``
context using ``ALINT_IGNORE``.


Not everything it checks is documented, and it does not check everything
that we like yet. But it's a start. Bug reports are welcome. Feature requests
prefer to be accompanied by a patch :-)
