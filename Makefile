default: update_version test

Makefile.version: FORCE
	@echo "FILE_VERSION = `sed -e 's/ .*//;1q' CHANGES.rst`" \
	  > Makefile.version.tmp
	@echo "GIT_VERSION = `git describe --tags --match \
	  'v[0-9]*' --abbrev=4 HEAD 2>/dev/null | sed -e s/^v//`" \
	  >> Makefile.version.tmp
	@cmp Makefile.version Makefile.version.tmp >/dev/null || \
	  mv Makefile.version.tmp Makefile.version
	@$(RM) -f Makefile.version.tmp
-include Makefile.version

install: Makefile.version
	python setup.py install

test:
	which flake8.3 >/dev/null && \
	  find . -name '*.py' | xargs -d\\n flake8.3 || true; echo
	python3 -m asterisklint.alinttest discover --pattern='test_*.py'

update_version:
	echo '$(GIT_VERSION)' | grep -Fq '$(FILE_VERSION)'  # startswith..
	sed -i -e "s/^version_str = .*/version_str = '$(FILE_VERSION)'/" \
	  asterisklint/alintver.py

.PHONY: FORCE default install test update_version
