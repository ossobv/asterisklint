.PHONY: test
test:
	which flake8.3 >/dev/null && \
	  find . -name '*.py' | xargs -d\\n flake8.3 || true; echo
	python3 -m asterisklint.alinttest discover --pattern='test_*.py'

.PHONY: test1
test1:
	python3 ./test1.py ./tests/extensions.conf
