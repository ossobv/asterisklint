FLAKE8 = $(shell which flake8.3 flake8 true 2>/dev/null | head -n1)
PYTHON = python3

default: update_version test

Makefile.version: FORCE
	# DEB/FILE version:     0.3.0~rc2 <-- canonical
	# GIT tag version:      v0.3.0_rc2
	# PyPI/PEP440 version:  0.3.0rc2
	@echo "FILE_VERSION = $$(sed -e 's/ .*//;1q' CHANGES.rst)" \
	  > Makefile.version.tmp
	@echo "GIT_VERSION = $$(git describe --tags --match \
	  'v[0-9]*' --abbrev=4 HEAD 2>/dev/null | \
	  sed -e 's/^v//;s/_/~/;s/-/+/')" \
	  >> Makefile.version.tmp
	@cmp Makefile.version Makefile.version.tmp >/dev/null || \
	  mv Makefile.version.tmp Makefile.version
	@$(RM) -f Makefile.version.tmp
	@cat Makefile.version
-include Makefile.version

install: Makefile.version
	$(PYTHON) setup.py install

test:
	find . -name '*.py' | xargs -d\\n $(FLAKE8) || true; echo
	$(PYTHON) -m asterisklint.alinttest discover -v --pattern='test_*.py'

license_turds:
	find . -name '*.py' -print0 | xargs -0 grep -L '^# Copyright (C)' | \
	  while read f; do t=`mktemp`; \
	  ( head -n15 setup.py; cat "$$f" ) > "$$t"; mv "$$t" "$$f"; done

pypi_upload: update_version
	# Call `make pypi_upload` to ensure that the version is correctly set.
	echo -n 'Continue uploading to PyPI? ' && read x && test "$$x" = y
	$(PYTHON) setup.py sdist
	twine upload dist/$(shell ./scripts/asterisklint --version | \
			    head -n1 | sed -e 's/ /-/;s/$$/.tar.gz/')

update_version:
	echo '$(GIT_VERSION)' | grep -Fq '$(FILE_VERSION)'  # startswith..
	sed -i -e "s/^version_str = .*/version_str = '$(FILE_VERSION)'/" \
	  asterisklint/alintver.py

.PHONY: FORCE default install test pypi_upload update_version license_turds
