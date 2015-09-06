.PHONY: test
test:
	python3 -m unittest discover --pattern='test_*.py'

.PHONY: test1
test1:
	python3 ./test1.py ./tests/extensions.conf
