Web frontend
============

::

    $ mkvirtualenv --python=$(which python3) asterisklint-web
    $ pip install falcon
    $ pip install asterisklint


TODO
----

* Short explanation at the top.
* Move notes to below Evaluate.
* Checkboxes for eliminating certain warnings/errors.
* Proper count of issues per issue.
  - Also in URI: W<n> (bitmask of issue types shown)
* Store dialplans for future viewing. (Optional.)
  Also fill the textbox at once? Otherwise others cannot edit it easily.
  - H<hash>S<n> = store for 2**3 seconds
  - 13S = 2h
  - 16S = 18h
  - 18S = 3d
  - 21S = 24d
  - 24S = 6m
