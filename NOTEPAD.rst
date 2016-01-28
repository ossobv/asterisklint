DN:

- plain-config lint(?)
- func_odbc lint
- example modules.conf parser where load/noload/preload/autoload
  are the only valid variables
- eindelijk beginnen aan function args parsing...
- app-check   # dialplan-check zonder dp
- expr-check  # expression-check zonder app/func

NDN:

- voor zover ik weet gaan long lines prima goed (bug=8191), maaar de output toont max 1024 van een
  dialplan regel (of 256 voor ast 1.4)
- asterisk-style inheritance?
- dialplan match-by-cli
- asterisk heeft geen multiline config (wel een maxlen van 8191 (buf[8192] in config_text_file_load)
- multiline config kan wel mooi met var=x; var+=y (maar lastig voor linter :-/ )
- multiline comments tussen ;-- en --; -- gebruikt niemand afaik
- delegate globals lintage to Config lint
- create the possibility for Asterisk version differences
- allow warnings to be suppressed? (always-emit, emit-once, silence)
- wat voor soort warnings: error (skip/ignore/fail), warning (case
  fouten of schijnbaar/mogelijke inconsequentie)
