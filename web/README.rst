Web frontend
============

::

    $ mkvirtualenv --python=`which python3` asterisklint-web
    $ pip install falcon
    $ pip install asterisklint


TODO
----

* Prettify output.
  * Smaller code font
  * Highlight errors with red line.
  * Error descriptions formatted; in small warning/info/error boxes?
  * Linenumbers?

* Warn user about uploading sensitive data.

* On server response error we want notification to user.

* Store dialplans for future viewing. (Optional.)
